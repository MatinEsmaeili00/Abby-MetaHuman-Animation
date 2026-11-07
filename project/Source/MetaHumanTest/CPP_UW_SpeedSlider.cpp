// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_UW_SpeedSlider.h"

void UCPP_UW_SpeedSlider::NativeConstruct()
{
	Super::NativeConstruct();


	if (APlayerController* PC = GetOwningPlayer())
	{
		AbbyCharacter = Cast<ACPP_AbbyCharacter>(PC->GetPawn());
	}

	if (SpeedSlider)
	{
		SpeedSlider->OnValueChanged.Clear();
		SpeedSlider->OnValueChanged.AddDynamic(this,&UCPP_UW_SpeedSlider::HandleSliderChanged);
	}

	
}

void UCPP_UW_SpeedSlider::HandleSliderChanged(float NormalizedValue)
{
	const float NewSpeed = FMath::Clamp(NormalizedValue,0.f,1.f);
	AbbyCharacter->Speed = NewSpeed;
}
