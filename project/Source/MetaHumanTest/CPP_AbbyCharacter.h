// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/SpringArmComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "TaskSyncManager.h"
#include "CPP_AbbyCharacter.generated.h"

UCLASS()
class METAHUMANTEST_API ACPP_AbbyCharacter : public APawn
{
	GENERATED_BODY()

public:
	// Sets default values for this pawn's properties
	ACPP_AbbyCharacter();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;




public:
	UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Properties")
	float Speed{};


};
