// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/Button.h"
#include "CPP_UW_PawnSwitcher.generated.h"

/**
 * 
 */

UCLASS()
class METAHUMANTEST_API UCPP_UW_PawnSwitcher : public UUserWidget
{
	GENERATED_BODY()

	virtual void NativeConstruct() override;

public:
	


	
protected:

	UPROPERTY(meta = (BindWidget))
	UButton* SwitchPawnUpBtn;

	UPROPERTY(meta = (BindWidget))
	UButton* SwitchPawnDownBtn;

	UFUNCTION()
	void OnSwitchPawnUpClicked();

	UFUNCTION()
	void OnSwitchPawnDownClicked();

	
	
};
