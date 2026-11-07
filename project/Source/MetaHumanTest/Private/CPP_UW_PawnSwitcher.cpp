// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_UW_PawnSwitcher.h"

#include "WCPP_AnimationTimeline.h"
#include "Components/Button.h"
#include "MetaHumanTest/CPP_PlayerController.h"

void UCPP_UW_PawnSwitcher::NativeConstruct()
{
	Super::NativeConstruct();


	if (SwitchPawnUpBtn)
	{
		SwitchPawnUpBtn->OnClicked.AddDynamic(this, &UCPP_UW_PawnSwitcher::OnSwitchPawnUpClicked);
	}

	if (SwitchPawnDownBtn)
	{
		SwitchPawnDownBtn->OnClicked.AddDynamic(this, &UCPP_UW_PawnSwitcher::OnSwitchPawnDownClicked);
	}
	
}

void UCPP_UW_PawnSwitcher::OnSwitchPawnUpClicked()
{
	ACPP_PlayerController* PC =
	Cast<ACPP_PlayerController>(GetOwningPlayer());

	//PC->PC_PlayerPlaceHolders
	
}

void UCPP_UW_PawnSwitcher::OnSwitchPawnDownClicked()
{
	ACPP_PlayerController* PC =
Cast<ACPP_PlayerController>(GetOwningPlayer());
}
