// Anatomy View component: peel a character from the outside in (skin -> muscles -> skeleton) with one value,
// like an anatomy app. Put it on the pawn; UI (sliders / buttons) only calls SetRevealDepth / ShowLayer.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Components/SkinnedMeshComponent.h"
#include "AnatomyViewComp.generated.h"

class UMeshComponent;
class UMaterialInterface;
class UMaterialInstanceDynamic;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAnatomyRevealDepthChanged, float, RevealDepth);

/** One anatomy layer, listed from the outside in. */
USTRUCT(BlueprintType)
struct METAHUMANANATOMYLAYERS_API FAnatomyLayerDef
{
	GENERATED_BODY()

	FAnatomyLayerDef() = default;
	FAnatomyLayerDef(FName InLayerName, TArray<FName> InComponentNamesOrTags)
		: LayerName(InLayerName), ComponentNamesOrTags(MoveTemp(InComponentNamesOrTags)) {}

	/** Display name (for UI and ShowLayerByName). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Anatomy")
	FName LayerName;

	/** Mesh components belong to this layer if their component name or one of their component tags is in this list.
	 *  The first (outermost) layer also gets every visible mesh that no other layer claims (body, face, hair, clothes...). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Anatomy")
	TArray<FName> ComponentNamesOrTags;
};

/** How one material slot is faded. */
USTRUCT()
struct FAnatomyFadeSlot
{
	GENERATED_BODY()

	UPROPERTY() TObjectPtr<UMaterialInterface> Original = nullptr;
	/** MID with the fade parameter; null means the slot is swapped to HiddenMaterial while the layer is not fully opaque. */
	UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> Fader = nullptr;
	/** Name of the parameter driven on Fader (Fade or Opacity). */
	UPROPERTY() FName Parameter;
	/** Value of Parameter at full opacity (Opacity params keep their authored strength). */
	UPROPERTY() float FullValue = 1.f;
};

/** One mesh component managed by a layer. */
USTRUCT()
struct FAnatomyFadeTarget
{
	GENERATED_BODY()

	UPROPERTY() TWeakObjectPtr<UMeshComponent> Mesh;
	UPROPERTY() TArray<FAnatomyFadeSlot> Slots;
	UPROPERTY() EVisibilityBasedAnimTickOption OriginalTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPose;

	float AppliedOpacity = -1.f;
	bool bFadersOn = false;
};

USTRUCT()
struct FAnatomyLayerRuntime
{
	GENERATED_BODY()

	UPROPERTY() FName LayerName;
	UPROPERTY() TArray<FAnatomyFadeTarget> Targets;
	float Opacity = 1.f;
};

/**
 * Reveal depth 0 = whole character, 1 = only the innermost layer.
 * With the default layers: 0 = skin, 0.5 = muscles, 1 = skeleton. In between, the outer layer fades out
 * (dithered via the material's "Fade" parameter, which MetaHuman skin/eye/teeth/hair materials already have)
 * and the inner layers fade in during the first part of the slider.
 * Fully faded meshes are hidden; skeletal meshes that are hidden keep ticking so Leader Pose followers keep animating.
 */
UCLASS(ClassGroup=(Anatomy), meta=(BlueprintSpawnableComponent), DisplayName="Anatomy View")
class METAHUMANANATOMYLAYERS_API UAnatomyViewComp : public UActorComponent
{
	GENERATED_BODY()

public:
	UAnatomyViewComp();

	/** Layers from the outside in. Defaults: Skin (everything else), Muscles (MuscleMesh / MusclePart), Skeleton (SkeletonMesh / SkeletonPart). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Anatomy")
	TArray<FAnatomyLayerDef> Layers;

	/** Scalar parameter that fades a material (1 = visible, 0 = gone). MetaHuman materials call it "Fade". */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Anatomy|Materials")
	FName FadeParameterName = TEXT("Fade");

	/** Used on translucent slots without a Fade parameter (e.g. MetaHuman eyelash cards, eye fluid): scaled by the layer opacity. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Anatomy|Materials")
	FName OpacityParameterName = TEXT("Opacity");

	/** Material for slots that have neither parameter (e.g. MetaHuman eye occlusion shell) while their layer is fading. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Anatomy|Materials")
	TSoftObjectPtr<UMaterialInterface> HiddenMaterial;

	/** Components with this tag are never touched. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Anatomy")
	FName IgnoreTag = TEXT("AnatomyIgnore");

	/** Reveal depth at BeginPlay. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Anatomy", meta=(ClampMin="0", ClampMax="1"))
	float InitialRevealDepth = 0.f;

	/** How fast ShowLayer animates (reveal depth per second). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Anatomy", meta=(ClampMin="0.01"))
	float TransitionSpeed = 1.5f;

	/** Inner layers fade in over this fraction of the first transition (0 = pop in at once). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Anatomy", meta=(ClampMin="0", ClampMax="1"))
	float InnerLayerFadeIn = 0.35f;

	/** Grooms (hair strands) are hidden once their layer is below this opacity: dithered strands look noisy. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Anatomy", meta=(ClampMin="0", ClampMax="1"))
	float HideGroomsBelowOpacity = 0.5f;

	/** Fires whenever the reveal depth changes (slider drag or animated ShowLayer). */
	UPROPERTY(BlueprintAssignable, Category="Anatomy")
	FOnAnatomyRevealDepthChanged OnRevealDepthChanged;

	/** 0 = whole character, 1 = innermost layer only. bAnimate eases there at TransitionSpeed. */
	UFUNCTION(BlueprintCallable, Category="Anatomy")
	void SetRevealDepth(float Depth, bool bAnimate = false);

	/** Animate so that layer LayerIndex (0 = outermost) is the outermost visible one. */
	UFUNCTION(BlueprintCallable, Category="Anatomy")
	void ShowLayer(int32 LayerIndex);

	UFUNCTION(BlueprintCallable, Category="Anatomy")
	void ShowLayerByName(FName LayerName);

	UFUNCTION(BlueprintPure, Category="Anatomy")
	float GetRevealDepth() const { return CurrentDepth; }

	/** Reveal depth at which LayerIndex is fully exposed. */
	UFUNCTION(BlueprintPure, Category="Anatomy")
	float GetLayerDepth(int32 LayerIndex) const;

	UFUNCTION(BlueprintPure, Category="Anatomy")
	int32 GetNumLayers() const { return Layers.Num(); }

	UFUNCTION(BlueprintPure, Category="Anatomy")
	float GetLayerOpacity(int32 LayerIndex) const;

	/** Re-scan the owner's mesh components (call after adding/removing/swapping meshes at runtime). */
	UFUNCTION(BlueprintCallable, Category="Anatomy")
	void RefreshLayers();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	void BuildRuntime();
	void RestoreAll();
	void ApplyDepth(float Depth);
	void ApplyOpacity(FAnatomyFadeTarget& Target, float Opacity);
	int32 FindLayerFor(const UMeshComponent* Mesh) const;
	float ComputeLayerOpacity(int32 LayerIndex, float Depth) const;

	UPROPERTY(Transient)
	TArray<FAnatomyLayerRuntime> Runtime;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> LoadedHiddenMaterial = nullptr;

	float CurrentDepth = 0.f;
	float TargetDepth = 0.f;
	bool bBuilt = false;
};
