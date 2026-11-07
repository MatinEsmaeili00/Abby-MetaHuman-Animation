// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_MouseFunctionComp.h"

#include <gsl/pointers>

#include "SWarningOrErrorBox.h"

// Sets default values for this component's properties
UCPP_MouseFunctionComp::UCPP_MouseFunctionComp()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;

	// ...
}


// Called when the game starts
void UCPP_MouseFunctionComp::BeginPlay()
{
	Super::BeginPlay();
	// ...


	if (AActor* Owner = GetOwner())
	{
		SpringArmComponent = Owner->FindComponentByClass<USpringArmComponent>();
		if (SpringArmComponent)
		{
			CurrentArmRot = SpringArmComponent->GetRelativeRotation();

			// 🔹 Initialize our zoom distance from the existing arm length
			CurrentCameraDistance = SpringArmComponent->TargetArmLength;
		}
		else
		{
			UE_LOG(LogTemp, Warning, TEXT("I didn't find the Spring Arm Component!"));
		}
	}
	else
	{
		UE_LOG(LogTemp,Warning,TEXT("I coudn't get the Owner !!") );
	}
	
}


// Called every frame
void UCPP_MouseFunctionComp::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// ...
}

void UCPP_MouseFunctionComp::OrbitFromMouse(const FVector2D& MouseDelta)
{

	CurrentArmRot.Yaw += MouseDelta.X*YawSpeedDegPerPx;
	CurrentArmRot.Pitch +=MouseDelta.Y*PitchSpeedDegPerPx;

	SpringArmComponent->SetRelativeRotation(CurrentArmRot);
}

void UCPP_MouseFunctionComp::ZoomCamera(float AxisValue)
{
	if (!SpringArmComponent || FMath::IsNearlyZero(AxisValue))
	{
		return;
	}

	// Positive AxisValue → zoom in (shorter arm)
	// Negative AxisValue → zoom out (longer arm)
	const float NewDistance = CurrentCameraDistance - AxisValue * ZoomSpeed;

	// Clamp between min/max
	CurrentCameraDistance = FMath::Clamp(NewDistance, MinZoom, MaxZoom);

	// Apply to spring arm
	SpringArmComponent->TargetArmLength = CurrentCameraDistance;

	// Optional debug
	// UE_LOG(LogTemp, Log, TEXT("Zoom: Axis=%f Distance=%f"), AxisValue, CurrentCameraDistance);
}

void UCPP_MouseFunctionComp::PanFromMouse(const FVector2D& MouseDelta)
{
	if (!SpringArmComponent)
	{
		return;
	}

	// Use camera rotation so pan feels screen-space
	const FRotator CamRot = SpringArmComponent->GetComponentRotation();
	const FVector Right   = FRotationMatrix(CamRot).GetScaledAxis(EAxis::Y);
	const FVector Up      = FRotationMatrix(CamRot).GetScaledAxis(EAxis::Z);

	// Build a world-space delta from mouse movement
	// const FVector WorldDelta =
	// 	(Right * MouseDelta.X + Up * -MouseDelta.Y) * PanSpeed;

	const FVector WorldDelta =
	(Right * MouseDelta.X + Up * MouseDelta.Y) * PanSpeed;


	// Convert current relative location to world-ish adjust, then back as just an offset
	FVector NewRelLocation = SpringArmComponent->GetRelativeLocation();
	NewRelLocation += WorldDelta;

	SpringArmComponent->SetRelativeLocation(NewRelLocation);
}


// CPP_MouseFunctionComp.cpp
void UCPP_MouseFunctionComp::SyncFromCurrentSpringArm()
{
	if (!SpringArmComponent) SpringArmComponent = GetOwner()->FindComponentByClass<USpringArmComponent>();
	if (!SpringArmComponent) return;

	// Example: whatever variables you use as baseline
	CurrentCameraDistance = SpringArmComponent->TargetArmLength;
	CurrentArmRot    = SpringArmComponent->GetRelativeRotation();
	// CachedSocketOffset = SpringArmComponent->SocketOffset;
	// CachedTargetOffset = SpringArmComponent->TargetOffset;
	//
	// // If you have drag state
	// bIsDragging = false;
}

