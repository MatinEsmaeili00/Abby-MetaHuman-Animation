// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/MeshComponent.h"

#include "CPP_UW_AnatomyViewSwitcher.generated.h"

/**
 * 
 */


class UButton;
class UGroomComponent;
class UGroomAsset;
class USlider;
UCLASS()
class METAHUMANTEST_API UCPP_UW_AnatomyViewSwitcher : public UUserWidget
{
	GENERATED_BODY()




	protected:
	virtual void NativeConstruct() override;

	// This name MUST match your widget variable name if you want BindWidget to work.
	UPROPERTY(meta = (BindWidget))
	UButton* AnatomyMetaHuman_Btn;

	UPROPERTY(meta = (BindWidget))
	USlider* AnatomyViewSwitcher_Slider;


	USkeletalMeshComponent* WholePartSM_Comp;
	USkeletalMeshComponent* SkeletonPartSM_Comp;
	USkeletalMeshComponent* FacePartSM_Comp;
	UGroomComponent* HairPartSM_Comp;


	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Groom")
	TObjectPtr<UGroomAsset> GroomStrandsAsset = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Groom")
	TObjectPtr<UGroomAsset> GroomCardsAsset = nullptr;

	UPROPERTY()
	bool bUsingCards = false;

	
	UMaterialInstanceDynamic* MID2;
	UMaterialInstanceDynamic* FaceMD2;
	UMaterialInstanceDynamic* HairMD2; 

public:
	// Set this in the Widget BP defaults (or from outside)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Spawn")
	TSubclassOf<APawn> PawnToSpawn;


private:

	
	
	UFUNCTION()
	void OnClick_SpawnAndPossess();

	UFUNCTION()
	void OnSliderValueChanged2(float Value);



	FVector PelvisWorld;
	UFUNCTION()
	const bool GetBoneWorldLocation(APawn* Pawn, FName BoneName
		, FVector& OutXform);

	
};
