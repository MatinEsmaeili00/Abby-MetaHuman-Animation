// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "CPP_MouseFunctionComp.generated.h"


UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class METAHUMANTEST_API UCPP_MouseFunctionComp : public UActorComponent
{
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	UCPP_MouseFunctionComp();

protected:
	// Called when the game starts
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;


	USpringArmComponent* SpringArmComponent;

	void OrbitFromMouse(const FVector2D& MouseDelta);
	void ZoomCamera(float AxisValue);



	// 🔹 NEW: pan from mouse (RMB)
	void PanFromMouse(const FVector2D& MouseDelta);
	

	UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Mouse Speed")
	float YawSpeedDegPerPx = 1.f;

	UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Mouse Speed")
	float PitchSpeedDegPerPx = 1.f;


	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="MetaHuman")
	TArray<AActor*> PlayerPlaceHolders;
	

	// 🔹 NEW: how fast we pan
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Pan")
	float PanSpeed = 1.0f;

	FRotator CurrentArmRot;
	
	// --- Zoom settings ---
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Zoom")
	float ZoomSpeed = 50.f;  // how fast we zoom per scroll step

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Zoom")
	float MinZoom = 50.f;   // closest

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Zoom")
	float MaxZoom = 1200.f;  // farthest

	// Current spring arm length we’re using
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Zoom")
	float CurrentCameraDistance = 0.f;



	// CPP_MouseFunctionComp.h
	UFUNCTION(BlueprintCallable)
	void SyncFromCurrentSpringArm();


	
};
