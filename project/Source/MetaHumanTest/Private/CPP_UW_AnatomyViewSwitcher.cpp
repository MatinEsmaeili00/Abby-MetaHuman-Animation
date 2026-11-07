// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_UW_AnatomyViewSwitcher.h"
#include "Components/Button.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/SpringArmComponent.h"
#include "MetaHumanTest/CPP_MouseFunctionComp.h"
#include "GroomComponent.h"
#include "Components/Slider.h"
#include "Components/SkeletalMeshComponent.h"


void UCPP_UW_AnatomyViewSwitcher::NativeConstruct()
{
	Super::NativeConstruct();

	if (AnatomyMetaHuman_Btn)
	{
		AnatomyMetaHuman_Btn->OnClicked.AddDynamic(this, &UCPP_UW_AnatomyViewSwitcher::OnClick_SpawnAndPossess);
	}

	if (AnatomyViewSwitcher_Slider)
	{
		AnatomyViewSwitcher_Slider->OnValueChanged.AddDynamic(this,&UCPP_UW_AnatomyViewSwitcher::OnSliderValueChanged2);	
	}
	


	
}



void UCPP_UW_AnatomyViewSwitcher::OnClick_SpawnAndPossess()
{
	APlayerController* PC = GetOwningPlayer();
	if (!PC) return;

	APawn* Pawn = PC->GetPawn();
	if (!Pawn) return;


	// 0. Finding parts of the metahuman like SkeletalMeshComponents and ...
	TArray<USkeletalMeshComponent*> SkeletalMeshComponents;

	Pawn->GetComponents<USkeletalMeshComponent>(SkeletalMeshComponents);

	for (USkeletalMeshComponent* Mesh:SkeletalMeshComponents)
	{
		if (Mesh && Mesh->ComponentHasTag("WholePart"))
		{
			WholePartSM_Comp = Mesh;

			UE_LOG(LogTemp, Warning, TEXT("Mesh: %s | Asset:%s | Tags: [WholePart]"),
	   *Mesh->GetName(),*Mesh->GetSkeletalMeshAsset()->GetName()
   );
		}
		if (Mesh && Mesh->ComponentHasTag("SkeletonPart"))
		{
			SkeletonPartSM_Comp = Mesh;

			UE_LOG(LogTemp, Warning, TEXT("Mesh: %s | Asset:%s | Tags: [SkeletonPart]"),
	   *Mesh->GetName(),*Mesh->GetSkeletalMeshAsset()->GetName()
   );
		}
		if (Mesh && Mesh->ComponentHasTag("FacePart"))
		{
			FacePartSM_Comp = Mesh;

			UE_LOG(LogTemp, Warning, TEXT("Mesh: %s | Asset:%s | Tags: [FacePart]"),
	   *Mesh->GetName(),*Mesh->GetSkeletalMeshAsset()->GetName()
   );
		}
		
	}

	// 0.1 Finding the Hair part and have it in the reference
	TArray<UGroomComponent*> GroomComponents;
	Pawn->GetComponents<UGroomComponent>(GroomComponents);
	for (UGroomComponent* GroomComponent:GroomComponents)
	{
		if (GroomComponent && GroomComponent->ComponentHasTag("HairPart"))
		{
			HairPartSM_Comp = GroomComponent;
			
			UE_LOG(LogTemp, Warning, TEXT("Mesh: %s | Tags: [HairPart]"),
	   *GroomComponent->GetName());
		}
	}

	
	

	// 1. Get pelvis world locations & fixing the location
	 const FVector WholePelvisWS =
		WholePartSM_Comp->GetBoneLocation(TEXT("pelvis"), EBoneSpaces::WorldSpace);

	FVector EditedWholePelvisWS = FVector(WholePelvisWS.X,WholePelvisWS.Y,10);
	
	SkeletonPartSM_Comp->SetRelativeLocation(EditedWholePelvisWS, true);


	
	const FVector PartPelvisWS =
		SkeletonPartSM_Comp->GetBoneLocation(TEXT("pelvis"), EBoneSpaces::WorldSpace);
	
	// 2. Compute delta needed to align them
	const FVector Delta = WholePelvisWS - PartPelvisWS;
	
	// 3. Apply delta to the component WORLD location
	SkeletonPartSM_Comp->SetWorldLocation(
		SkeletonPartSM_Comp->GetComponentLocation() + Delta
	);



	// // 2. setting and making Dynamic material
	// const int32 NumWholePartsMats = WholePartSM_Comp->GetNumMaterials();
	// for (int32 i = 0; i < NumWholePartsMats; i++)
	// {
	// 	MID = WholePartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
	//
	//
	// }
	//
	// // 2.1 setting and making dynamic material for Face part
	// const int32 NumFaceMats = FacePartSM_Comp->GetNumMaterials();
	// for (int32 i = 0; i < NumFaceMats; i++)
	// {
	// 	// Creates a MID for slot i AND assigns it to slot i
	// 	FaceMD = FacePartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
	// 	
	// }
	//
	// // 2.2 setting and making dynamic material for Face part
	// if (HairPartSM_Comp)
	// {
	// 	const int32 NumHairMats = HairPartSM_Comp->GetNumMaterials();
	// 	for (int32 i = 0; i < NumHairMats; i++)
	// 	{
	// 		// Creates a MID for slot i AND assigns it to slot i
	// 		HairMD = HairPartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
	// 		
	// 	}
	// }
	//


	// 2. setting and making Dynamic material
	const int32 NumWholePartsMats = WholePartSM_Comp->GetNumMaterials();
	for (int32 i = 0; i < NumWholePartsMats; i++)
	{
		 MID2 = WholePartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);

		if (MID2)
		{
			float DummyValue;
			if (MID2->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Fade")), DummyValue))
			{
				// ✅ Parameter exists
				MID2->SetScalarParameterValue(TEXT("Fade"), 0.2);
			}
		}
	}

	// 2.1 setting and making dynamic material for Face part
	const int32 NumFaceMats = FacePartSM_Comp->GetNumMaterials();
	for (int32 i = 0; i < NumFaceMats; i++)
	{
		// Creates a MID for slot i AND assigns it to slot i
		 FaceMD2 = FacePartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
		if (FaceMD2)
		{
	
			float DummyValue;
			if (FaceMD2->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Fade")), DummyValue))
			{
				// ✅ Parameter exists
				FaceMD2->SetScalarParameterValue(TEXT("Fade"), 0.2);
			}
			
		}
	}
	
	// 2.2 setting and making dynamic material for Face part
	if (HairPartSM_Comp)
	{
		const int32 NumHairMats = HairPartSM_Comp->GetNumMaterials();
		for (int32 i = 0; i < NumHairMats; i++)
		{
			// Creates a MID for slot i AND assigns it to slot i
			 HairMD2 = HairPartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
			if (HairMD2)
			{
				float DummyValue;
				if (HairMD2->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Fade")), DummyValue))
				{
					// ✅ Parameter exists
					HairMD2->SetScalarParameterValue(TEXT("Fade"), 0.2);
				}
			
			}
		}
	}
	
	return;
}

// void UCPP_UW_AnatomyViewSwitcher::OnSliderValueChanged2(float Value)
// {
//
// 	
//
//
// 	
// 	// 2.1 setting and making dynamic material for Face part
// 	const int32 NumFaceMats = FacePartSM_Comp->GetNumMaterials();
// 	for (int32 i = 0; i < NumFaceMats; i++)
// 	{
//
// 	
// 		// Creates a MID for slot i AND assigns it to slot i
// 		//UMaterialInstanceDynamic* FaceMD = FacePartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
// 		if (FaceMD2)
// 		{
// 	
// 			float DummyValue;
// 			if (FaceMD2->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Fade")), DummyValue))
// 			{
// 				// ✅ Parameter exists
// 				FaceMD2->SetScalarParameterValue(TEXT("Fade"), Value);
// 			}
// 			else
// 			{
// 				UE_LOG(LogTemp, Warning, TEXT("[FaceFade] is NULL"));
// 			}
// 			
// 		}
// 	}
// 	
// 	// 2. setting and making Dynamic material
// 	const int32 NumWholePartsMats = WholePartSM_Comp->GetNumMaterials();
// 	for (int32 i = 0; i < NumWholePartsMats; i++)
// 	{
// 		//UMaterialInstanceDynamic* MID = WholePartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
// 	
// 		if (MID2)
// 		{
// 			float DummyValue;
// 			if (MID2->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Fade")), DummyValue))
// 			{
// 				// ✅ Parameter exists
// 				MID2->SetScalarParameterValue(TEXT("Fade"), Value);
// 			}
// 			
// 			else
// 			{
// 				UE_LOG(LogTemp, Warning, TEXT("[MIDFade] is NULL"));
// 			}
// 		}
// 	}
// 	
// 	
// 	
// 	// 2.2 setting and making dynamic material for Face part
// 	if (HairPartSM_Comp)
// 	{
// 		const int32 NumHairMats = HairPartSM_Comp->GetNumMaterials();
// 		for (int32 i = 0; i < NumHairMats; i++)
// 		{
// 			// Creates a MID for slot i AND assigns it to slot i
// 			//UMaterialInstanceDynamic* HairMD = HairPartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
// 			if (HairMD2)
// 			{
// 				float DummyValue;
// 				if (HairMD2->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Fade")), DummyValue))
// 				{
// 					// ✅ Parameter exists
// 					HairMD2->SetScalarParameterValue(TEXT("Fade"), Value);
// 				}
// 				
// 				else
// 				{
// 					UE_LOG(LogTemp, Warning, TEXT("[HairFade] is NULL"));
// 				}
// 				
// 			
// 			}
// 		}
// 	}
// 	return;
// 	
// }
//


void UCPP_UW_AnatomyViewSwitcher::OnSliderValueChanged2(float Value)
{

	


		APlayerController* PC = GetOwningPlayer();
	if (!PC) return;

	APawn* Pawn = PC->GetPawn();
	if (!Pawn) return;


	// 0. Finding parts of the metahuman like SkeletalMeshComponents and ...
	TArray<USkeletalMeshComponent*> SkeletalMeshComponents;

	Pawn->GetComponents<USkeletalMeshComponent>(SkeletalMeshComponents);

	for (USkeletalMeshComponent* Mesh:SkeletalMeshComponents)
	{
		if (Mesh && Mesh->ComponentHasTag("WholePart"))
		{
			WholePartSM_Comp = Mesh;

			UE_LOG(LogTemp, Warning, TEXT("Mesh: %s | Asset:%s | Tags: [WholePart]"),
	   *Mesh->GetName(),*Mesh->GetSkeletalMeshAsset()->GetName()
   );
		}
		if (Mesh && Mesh->ComponentHasTag("SkeletonPart"))
		{
			SkeletonPartSM_Comp = Mesh;

			UE_LOG(LogTemp, Warning, TEXT("Mesh: %s | Asset:%s | Tags: [SkeletonPart]"),
	   *Mesh->GetName(),*Mesh->GetSkeletalMeshAsset()->GetName()
   );
		}
		if (Mesh && Mesh->ComponentHasTag("FacePart"))
		{
			FacePartSM_Comp = Mesh;

			UE_LOG(LogTemp, Warning, TEXT("Mesh: %s | Asset:%s | Tags: [FacePart]"),
	   *Mesh->GetName(),*Mesh->GetSkeletalMeshAsset()->GetName()
   );
		}
		
	}

	// 0.1 Finding the Hair part and have it in the reference
	TArray<UGroomComponent*> GroomComponents;
	Pawn->GetComponents<UGroomComponent>(GroomComponents);
	for (UGroomComponent* GroomComponent:GroomComponents)
	{
		if (GroomComponent && GroomComponent->ComponentHasTag("HairPart"))
		{
			HairPartSM_Comp = GroomComponent;
			
			UE_LOG(LogTemp, Warning, TEXT("Mesh: %s | Tags: [HairPart]"),
	   *GroomComponent->GetName());
		}
	}

	
	

	// 1. Get pelvis world locations & fixing the location
	 const FVector WholePelvisWS =
		WholePartSM_Comp->GetBoneLocation(TEXT("pelvis"), EBoneSpaces::WorldSpace);

	FVector EditedWholePelvisWS = FVector(WholePelvisWS.X,WholePelvisWS.Y,10);
	
	SkeletonPartSM_Comp->SetRelativeLocation(EditedWholePelvisWS, true);


	
	const FVector PartPelvisWS =
		SkeletonPartSM_Comp->GetBoneLocation(TEXT("pelvis"), EBoneSpaces::WorldSpace);
	
	// 2. Compute delta needed to align them
	const FVector Delta = WholePelvisWS - PartPelvisWS;
	
	// 3. Apply delta to the component WORLD location
	SkeletonPartSM_Comp->SetWorldLocation(
		SkeletonPartSM_Comp->GetComponentLocation() + Delta
	);



	// // 2. setting and making Dynamic material
	// const int32 NumWholePartsMats = WholePartSM_Comp->GetNumMaterials();
	// for (int32 i = 0; i < NumWholePartsMats; i++)
	// {
	// 	MID = WholePartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
	//
	//
	// }
	//
	// // 2.1 setting and making dynamic material for Face part
	// const int32 NumFaceMats = FacePartSM_Comp->GetNumMaterials();
	// for (int32 i = 0; i < NumFaceMats; i++)
	// {
	// 	// Creates a MID for slot i AND assigns it to slot i
	// 	FaceMD = FacePartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
	// 	
	// }
	//
	// // 2.2 setting and making dynamic material for Face part
	// if (HairPartSM_Comp)
	// {
	// 	const int32 NumHairMats = HairPartSM_Comp->GetNumMaterials();
	// 	for (int32 i = 0; i < NumHairMats; i++)
	// 	{
	// 		// Creates a MID for slot i AND assigns it to slot i
	// 		HairMD = HairPartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
	// 		
	// 	}
	// }
	//


	// 2. setting and making Dynamic material
	const int32 NumWholePartsMats = WholePartSM_Comp->GetNumMaterials();
	for (int32 i = 0; i < NumWholePartsMats; i++)
	{
		 MID2 = WholePartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);

		if (MID2)
		{
			float DummyValue;
			if (MID2->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Fade")), DummyValue))
			{
				// ✅ Parameter exists
				MID2->SetScalarParameterValue(TEXT("Fade"), Value);
			}
		}
	}

	// 2.1 setting and making dynamic material for Face part
	const int32 NumFaceMats = FacePartSM_Comp->GetNumMaterials();
	for (int32 i = 0; i < NumFaceMats; i++)
	{
		// Creates a MID for slot i AND assigns it to slot i
		 FaceMD2 = FacePartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
		if (FaceMD2)
		{
	
			float DummyValue;
			if (FaceMD2->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Fade")), DummyValue))
			{
				// ✅ Parameter exists
				FaceMD2->SetScalarParameterValue(TEXT("Fade"), Value);
			}
			
		}
	}
	
	// 2.2 setting and making dynamic material for Face part
	if (HairPartSM_Comp)
	{
		if (Value<.9f)
		{
			if (GroomCardsAsset&& GroomStrandsAsset)
			{
				if (!bUsingCards)
				{
					HairPartSM_Comp->SetGroomAsset(GroomCardsAsset);
					bUsingCards = true;
				}
			}
		}else
		{
			if (GroomCardsAsset&& GroomStrandsAsset)
			{
				if (bUsingCards)
				{
					HairPartSM_Comp->SetGroomAsset(GroomStrandsAsset);
					bUsingCards = false;
				}
			}
		}	
		

		
		const int32 NumHairMats = HairPartSM_Comp->GetNumMaterials();
		for (int32 i = 0; i < NumHairMats; i++)
		{
			// Creates a MID for slot i AND assigns it to slot i
			 HairMD2 = HairPartSM_Comp->CreateAndSetMaterialInstanceDynamic(i);
			if (HairMD2)
			{
				float DummyValue;
				if (HairMD2->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Fade")), DummyValue))
				{
					// ✅ Parameter exists
					HairMD2->SetScalarParameterValue(TEXT("Fade"), Value);
				}
			
			}
		}
	}
	
	return;
}




const bool UCPP_UW_AnatomyViewSwitcher::GetBoneWorldLocation(APawn* Pawn, FName BoneName, FVector& OutXform)
{

	if (!Pawn) return false;

	USkeletalMeshComponent* Mesh = Pawn->FindComponentByClass<USkeletalMeshComponent>();
	if (!Mesh) return false;

	// Bone transform in component space, then convert to world
	FVector PelvisWorld2 = Mesh->GetBoneLocation(TEXT("pelvis")); // world space
	OutXform = PelvisWorld2;
	return true;
}

