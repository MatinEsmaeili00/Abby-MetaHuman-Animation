#include "AnatomyViewComp.h"

#include "MetaHumanAnatomyLayers.h"
#include "Components/MeshComponent.h"
#include "Components/SkinnedMeshComponent.h"
#include "GameFramework/Actor.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/MaterialInterface.h"

namespace AnatomyView
{
	// Grooms live in the HairStrands plugin; match by class name so this module doesn't depend on it.
	static bool IsGroom(const UMeshComponent* Mesh)
	{
		for (const UClass* Class = Mesh ? Mesh->GetClass() : nullptr; Class; Class = Class->GetSuperClass())
		{
			if (Class->GetFName() == TEXT("GroomComponent"))
			{
				return true;
			}
		}
		return false;
	}

	static constexpr float Opaque = 0.999f;
	static constexpr float Gone = 0.001f;
}

UAnatomyViewComp::UAnatomyViewComp()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false; // only ticks while animating between layers

	HiddenMaterial = TSoftObjectPtr<UMaterialInterface>(FSoftObjectPath(TEXT("/MetaHumanAnatomyLayers/Anatomy/Materials/M_Anatomy_Hidden.M_Anatomy_Hidden")));

	Layers.Emplace(TEXT("Skin"),     TArray<FName>{ TEXT("SkinPart") });
	Layers.Emplace(TEXT("Muscles"),  TArray<FName>{ TEXT("MuscleMesh"), TEXT("MusclePart") });
	Layers.Emplace(TEXT("Skeleton"), TArray<FName>{ TEXT("SkeletonMesh"), TEXT("SkeletonPart") });
}

void UAnatomyViewComp::BeginPlay()
{
	Super::BeginPlay();

	LoadedHiddenMaterial = HiddenMaterial.LoadSynchronous();
	BuildRuntime();

	CurrentDepth = TargetDepth = FMath::Clamp(InitialRevealDepth, 0.f, 1.f);
	ApplyDepth(CurrentDepth);
}

void UAnatomyViewComp::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	// Removing just this component at runtime should leave the character as it found it.
	if (EndPlayReason == EEndPlayReason::Destroyed && GetOwner() && !GetOwner()->IsActorBeingDestroyed())
	{
		RestoreAll();
	}
	Super::EndPlay(EndPlayReason);
}

int32 UAnatomyViewComp::FindLayerFor(const UMeshComponent* Mesh) const
{
	for (int32 LayerIndex = 0; LayerIndex < Layers.Num(); ++LayerIndex)
	{
		for (const FName& Key : Layers[LayerIndex].ComponentNamesOrTags)
		{
			if (Mesh->GetFName() == Key || Mesh->ComponentHasTag(Key))
			{
				return LayerIndex;
			}
		}
	}
	return INDEX_NONE;
}

void UAnatomyViewComp::BuildRuntime()
{
	Runtime.Reset();
	Runtime.SetNum(Layers.Num());
	for (int32 LayerIndex = 0; LayerIndex < Layers.Num(); ++LayerIndex)
	{
		Runtime[LayerIndex].LayerName = Layers[LayerIndex].LayerName;
	}

	AActor* Owner = GetOwner();
	if (!Owner || Layers.Num() == 0)
	{
		bBuilt = true;
		return;
	}

	TArray<UMeshComponent*> Meshes;
	Owner->GetComponents<UMeshComponent>(Meshes);

	for (UMeshComponent* Mesh : Meshes)
	{
		if (!Mesh || Mesh->ComponentHasTag(IgnoreTag))
		{
			continue;
		}

		int32 LayerIndex = FindLayerFor(Mesh);
		if (LayerIndex == INDEX_NONE)
		{
			// Unclaimed meshes are the outer "skin" layer, but only ones that are actually shown in game
			// (skips editor-only helpers and parts the designer hid on purpose).
			if (!Mesh->IsVisible() || Mesh->bHiddenInGame)
			{
				continue;
			}
			LayerIndex = 0;
		}

		FAnatomyFadeTarget Target;
		Target.Mesh = Mesh;
		if (const USkinnedMeshComponent* Skinned = Cast<USkinnedMeshComponent>(Mesh))
		{
			Target.OriginalTickOption = Skinned->VisibilityBasedAnimTickOption;
		}

		const int32 NumMaterials = Mesh->GetNumMaterials();
		Target.Slots.SetNum(NumMaterials);
		for (int32 SlotIndex = 0; SlotIndex < NumMaterials; ++SlotIndex)
		{
			FAnatomyFadeSlot& Slot = Target.Slots[SlotIndex];
			Slot.Original = Mesh->GetMaterial(SlotIndex);
			if (!Slot.Original)
			{
				continue;
			}

			float Value = 0.f;
			// "Fade" counts only when it's the visibility fade (authored at 1). MetaHuman facial-hair cards use a
			// "Fade" that defaults to 0 for something else, so those fall through to Opacity / hidden.
			if (Slot.Original->GetScalarParameterValue(FHashedMaterialParameterInfo(FadeParameterName), Value) && Value > 0.5f)
			{
				Slot.Parameter = FadeParameterName;
				Slot.FullValue = 1.f;
			}
			else if (Slot.Original->GetScalarParameterValue(FHashedMaterialParameterInfo(OpacityParameterName), Value))
			{
				Slot.Parameter = OpacityParameterName;
				Slot.FullValue = Value;
			}

			if (!Slot.Parameter.IsNone())
			{
				Slot.Fader = UMaterialInstanceDynamic::Create(Slot.Original, Mesh);
			}
		}

		Runtime[LayerIndex].Targets.Add(MoveTemp(Target));
	}

	for (const FAnatomyLayerRuntime& Layer : Runtime)
	{
		FString Names;
		for (const FAnatomyFadeTarget& Target : Layer.Targets)
		{
			Names += Target.Mesh.IsValid() ? Target.Mesh->GetName() + TEXT(" ") : FString();
		}
		UE_LOG(LogAnatomyLayers, Log, TEXT("[%s] layer %s: %s"), *GetNameSafe(Owner), *Layer.LayerName.ToString(), *Names);
	}

	bBuilt = true;
}

void UAnatomyViewComp::RestoreAll()
{
	for (FAnatomyLayerRuntime& Layer : Runtime)
	{
		for (FAnatomyFadeTarget& Target : Layer.Targets)
		{
			Target.AppliedOpacity = -1.f;
			ApplyOpacity(Target, 1.f);
		}
	}
}

void UAnatomyViewComp::RefreshLayers()
{
	RestoreAll();
	BuildRuntime();
	ApplyDepth(CurrentDepth);
}

float UAnatomyViewComp::GetLayerDepth(int32 LayerIndex) const
{
	const int32 Num = Layers.Num();
	return Num <= 1 ? 0.f : FMath::Clamp(static_cast<float>(LayerIndex) / static_cast<float>(Num - 1), 0.f, 1.f);
}

float UAnatomyViewComp::GetLayerOpacity(int32 LayerIndex) const
{
	return Runtime.IsValidIndex(LayerIndex) ? Runtime[LayerIndex].Opacity : 0.f;
}

float UAnatomyViewComp::ComputeLayerOpacity(int32 LayerIndex, float Depth) const
{
	const int32 Num = Layers.Num();
	if (Num <= 1)
	{
		return 1.f - Depth;
	}

	const float Segment = 1.f / static_cast<float>(Num - 1);

	// Layer k fades out across [k, k+1] * Segment; the innermost layer never fades out.
	const float FadeOut = (LayerIndex == Num - 1)
		? 1.f
		: 1.f - FMath::Clamp((Depth - LayerIndex * Segment) / Segment, 0.f, 1.f);

	// Inner layers fade in while the outer one starts to go, so muscles that are bigger than the skin
	// don't pop through it the moment the slider moves.
	float FadeIn = 1.f;
	if (LayerIndex > 0)
	{
		FadeIn = InnerLayerFadeIn <= 0.f
			? (Depth > 0.f ? 1.f : 0.f)
			: FMath::Clamp(Depth / (InnerLayerFadeIn * Segment), 0.f, 1.f);
	}

	return FadeOut * FadeIn;
}

void UAnatomyViewComp::ApplyDepth(float Depth)
{
	for (int32 LayerIndex = 0; LayerIndex < Runtime.Num(); ++LayerIndex)
	{
		FAnatomyLayerRuntime& Layer = Runtime[LayerIndex];
		Layer.Opacity = ComputeLayerOpacity(LayerIndex, Depth);
		for (FAnatomyFadeTarget& Target : Layer.Targets)
		{
			ApplyOpacity(Target, Layer.Opacity);
		}
	}
	OnRevealDepthChanged.Broadcast(Depth);
}

void UAnatomyViewComp::ApplyOpacity(FAnatomyFadeTarget& Target, float Opacity)
{
	UMeshComponent* Mesh = Target.Mesh.Get();
	if (!Mesh)
	{
		return;
	}

	const float Effective = (AnatomyView::IsGroom(Mesh) && Opacity < HideGroomsBelowOpacity) ? 0.f : Opacity;
	if (FMath::IsNearlyEqual(Effective, Target.AppliedOpacity, 0.0005f))
	{
		return;
	}
	Target.AppliedOpacity = Effective;

	USkinnedMeshComponent* Skinned = Cast<USkinnedMeshComponent>(Mesh);

	if (Effective <= AnatomyView::Gone)
	{
		// Hidden meshes normally stop animating; keep the pose ticking so Leader Pose followers
		// (the muscle / skeleton layers follow Body) keep moving.
		if (Skinned)
		{
			Skinned->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
		}
		Mesh->SetVisibility(false);
		return;
	}

	if (!Mesh->IsVisible())
	{
		Mesh->SetVisibility(true);
	}
	if (Skinned)
	{
		Skinned->VisibilityBasedAnimTickOption = Target.OriginalTickOption;
	}

	if (Effective >= AnatomyView::Opaque)
	{
		// Fully opaque: back to the original materials (no dithering, original eye shell etc.).
		if (Target.bFadersOn)
		{
			for (int32 SlotIndex = 0; SlotIndex < Target.Slots.Num(); ++SlotIndex)
			{
				Mesh->SetMaterial(SlotIndex, Target.Slots[SlotIndex].Original);
			}
			Target.bFadersOn = false;
		}
		return;
	}

	if (!Target.bFadersOn)
	{
		for (int32 SlotIndex = 0; SlotIndex < Target.Slots.Num(); ++SlotIndex)
		{
			const FAnatomyFadeSlot& Slot = Target.Slots[SlotIndex];
			UMaterialInterface* Material = Slot.Fader ? Slot.Fader.Get() : (LoadedHiddenMaterial ? LoadedHiddenMaterial.Get() : Slot.Original.Get());
			Mesh->SetMaterial(SlotIndex, Material);
		}
		Target.bFadersOn = true;
	}

	for (const FAnatomyFadeSlot& Slot : Target.Slots)
	{
		if (Slot.Fader)
		{
			Slot.Fader->SetScalarParameterValue(Slot.Parameter, Slot.FullValue * Effective);
		}
	}
}

void UAnatomyViewComp::SetRevealDepth(float Depth, bool bAnimate)
{
	TargetDepth = FMath::Clamp(Depth, 0.f, 1.f);

	if (!bBuilt)
	{
		InitialRevealDepth = TargetDepth; // BeginPlay hasn't run yet
		return;
	}

	if (bAnimate)
	{
		SetComponentTickEnabled(true);
		return;
	}

	SetComponentTickEnabled(false);
	if (!FMath::IsNearlyEqual(CurrentDepth, TargetDepth))
	{
		CurrentDepth = TargetDepth;
		ApplyDepth(CurrentDepth);
	}
}

void UAnatomyViewComp::ShowLayer(int32 LayerIndex)
{
	if (Layers.IsValidIndex(LayerIndex))
	{
		SetRevealDepth(GetLayerDepth(LayerIndex), /*bAnimate*/ true);
	}
}

void UAnatomyViewComp::ShowLayerByName(FName LayerName)
{
	ShowLayer(Layers.IndexOfByPredicate([LayerName](const FAnatomyLayerDef& Def) { return Def.LayerName == LayerName; }));
}

void UAnatomyViewComp::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	CurrentDepth = FMath::FInterpConstantTo(CurrentDepth, TargetDepth, DeltaTime, TransitionSpeed);
	ApplyDepth(CurrentDepth);

	if (FMath::IsNearlyEqual(CurrentDepth, TargetDepth, KINDA_SMALL_NUMBER))
	{
		SetComponentTickEnabled(false);
	}
}
