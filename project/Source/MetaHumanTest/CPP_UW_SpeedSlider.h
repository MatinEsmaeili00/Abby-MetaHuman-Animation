// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "CPP_AbbyCharacter.h"
#include "Blueprint/UserWidget.h"
#include "Components/Slider.h"
#include "CPP_UW_SpeedSlider.generated.h"

/**
 * 
 */
UCLASS()
class METAHUMANTEST_API UCPP_UW_SpeedSlider : public UUserWidget
{
	GENERATED_BODY()



public:
	UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed")
	float MinSpeed = 0.f;

	UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Speed")
	float MaxSpeed = 100.f;

protected:
	UPROPERTY(meta=(BindWidgetOptional))
	USlider* SpeedSlider;

	virtual void NativeConstruct() override;

private:
	UFUNCTION()
	void HandleSliderChanged(float NormalizedValue);

	ACPP_AbbyCharacter* AbbyCharacter;
	
};
