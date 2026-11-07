// Fill out your copyright notice in the Description page of Project Settings.


#include "WCPP_AnimationTimeline.h"

#include "AnimationTimelineComp.h"
#include "Components/Button.h"
#include "Components/Slider.h"

void UWCPP_AnimationTimeline::NativeConstruct()
{
	Super::NativeConstruct();


	if (PlayBtn)
	{
		PlayBtn->OnClicked.AddDynamic(this, &UWCPP_AnimationTimeline::OnPlayClicked);
	}

	if (PauseBtn)
	{
		PauseBtn->OnClicked.AddDynamic(this, &UWCPP_AnimationTimeline::OnPauseClicked);
	}

	if (ReverseBtn)
	{
		ReverseBtn->OnClicked.AddDynamic(this, &UWCPP_AnimationTimeline::OnReverseClicked);
	}

	if (Slider_Time)
	{
		Slider_Time->OnValueChanged.AddDynamic(this, &UWCPP_AnimationTimeline::OnSliderValueChanged);


		// they are already being set in bp !
		//Slider_Time->SetMinValue(0.f);
		//Slider_Time->SetMaxValue(1.f);
		//Slider_Time->SetValue(0.f);
	}



	
}

void UWCPP_AnimationTimeline::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);

	TimelineComp= GetAnimationTimelineComp();

	
	if (TimelineComp && Slider_Time) // I have got the TimelineComp passed by Player Controller
	{
		Slider_Time->SetValue(TimelineComp->GetNormalizedTime());
	}
}


void UWCPP_AnimationTimeline::OnPlayClicked()
{
	TimelineComp= GetAnimationTimelineComp();
	if (TimelineComp)
	{
		TimelineComp->PlayForward();
	}
}

void UWCPP_AnimationTimeline::OnPauseClicked()
{
	TimelineComp= GetAnimationTimelineComp();
	if (TimelineComp)
	{
		TimelineComp->Pause();
	}
}

void UWCPP_AnimationTimeline::OnReverseClicked()
{
	TimelineComp= GetAnimationTimelineComp();
	if (TimelineComp)
	{
		TimelineComp->PlayReverse();
	}
}

void UWCPP_AnimationTimeline::OnSliderValueChanged(float Value)
{
	TimelineComp= GetAnimationTimelineComp();
	if (TimelineComp)
	{
		TimelineComp->SetNormalizedTime(Value);
	}
}

UAnimationTimelineComp* UWCPP_AnimationTimeline::GetAnimationTimelineComp()
{
	APawn* CurrentPawn = GetOwningPlayerPawn();
	if (!CurrentPawn)
	{
		return nullptr;
	}

	return CurrentPawn->FindComponentByClass<UAnimationTimelineComp>();

	
}
