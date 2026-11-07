// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "WCPP_AnimationTimeline.generated.h"

/**
 * 
 */


class UButton;
class USlider;
class UAnimationTimelineComp;


UCLASS()
class METAHUMANTEST_API UWCPP_AnimationTimeline : public UUserWidget
{
	GENERATED_BODY()

	
	virtual void NativeConstruct() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;


public:
	// I have got the TimelineComp passed by Player Controller
	UPROPERTY(BlueprintReadWrite, meta=(ExposeOnSpawn = "true"), Category="Timeline")
	UAnimationTimelineComp* TimelineComp = nullptr;




protected:
	
	// BindWidget = will auto-bind to Designer widgets with the same name
	UPROPERTY(meta = (BindWidget))
	UButton* PlayBtn;

	UPROPERTY(meta = (BindWidget))
	UButton* PauseBtn;

	UPROPERTY(meta = (BindWidget))
	UButton* ReverseBtn;

	UPROPERTY(meta = (BindWidget))
	USlider* Slider_Time;


	UFUNCTION()
	void OnPlayClicked();

	UFUNCTION()
	void OnPauseClicked();

	UFUNCTION()
	void OnReverseClicked();

	UFUNCTION()
	void OnSliderValueChanged(float Value);
	UAnimationTimelineComp* GetAnimationTimelineComp();
};
