// Fill out your copyright notice in the Description page of Project Settings.


#include "CPP_PlayerController.h"

#include "AnimationTimelineComp.h"
#include "CPP_PlayerPlaceHolderManagerA.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "WCPP_AnimationTimeline.h"
#include "Kismet/GameplayStatics.h"

void ACPP_PlayerController::BeginPlay()
{
	

	//bShowMouseCursor = true;

	bShowMouseCursor = true;

	FInputModeGameAndUI InputMode;
	InputMode.SetHideCursorDuringCapture(false);
	SetInputMode(InputMode);


	if (ULocalPlayer* LP = GetLocalPlayer())
	{
		if (UEnhancedInputLocalPlayerSubsystem* Subsys = LP->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
		{
			if (MouseManager)
			{
				Subsys->AddMappingContext(MouseManager, /*Priority*/1);
			}
		}
	}

	// if (SpeedSliderWidget)
	// {
	// 	SpeedSliderWidgetInstance = CreateWidget<UCPP_UW_SpeedSlider>(this,SpeedSliderWidget);
	// 	if (SpeedSliderWidgetInstance)
	// 	{
	// 		SpeedSliderWidgetInstance->AddToViewport(10);
	// 	}
	// }


	// UAnimationTimelineComp* TimelineComp = nullptr;
	//
	// //if (TargetMetaHuman)
	//
	// if (APawn* MyPawn = GetPawn())
	// {
	// 	TimelineComp = MyPawn->FindComponentByClass<UAnimationTimelineComp>();
	// }

	if (TimelineWidgetClass)
	{
		TimelineWidget = CreateWidget<UWCPP_AnimationTimeline>(this, TimelineWidgetClass);
		if (TimelineWidget)
		{
			// we don't need it anymore bc in the widget class I'm getting the current pawn and get access to the timeline component on it
			//TimelineWidget->TimelineComp = TimelineComp;  // 🔗 Pass the component reference 
			TimelineWidget->AddToViewport();
		}
	}
	
	if (AnatomyViewSwitcherWidgetClass)
	{
		AnatomyViewSwitcherWidget = CreateWidget<UCPP_UW_AnatomyViewSwitcher>(this, AnatomyViewSwitcherWidgetClass);
		if (AnatomyViewSwitcherWidget)
		{
			AnatomyViewSwitcherWidget->AddToViewport();
		}
	}

	if (PawnSwitcherWidgetClass)
	{
		PawnSwitcherWidget = CreateWidget<UCPP_UW_PawnSwitcher>(this, PawnSwitcherWidgetClass);
	if (PawnSwitcherWidget)
	{
		PawnSwitcherWidget->AddToViewport();
	}
	}


	ACPP_PlayerPlaceHolderManagerA* PlayerPlaceHolderManager =
		Cast<ACPP_PlayerPlaceHolderManagerA>
	(UGameplayStatics::GetActorOfClass(GetWorld(),
		APlayerCameraManager::StaticClass()));

	if (!PlayerPlaceHolderManager)
	{
		UE_LOG(LogTemp, Warning, TEXT("No PlayerPlaceholderManager found in level!"));
		
	}
	else
	{
		PC_PlayerPlaceHolders = PlayerPlaceHolderManager->PlayerPlaceHolders;
	}
	
}

void ACPP_PlayerController::SetupInputComponent()
{
	Super::SetupInputComponent();

	if (UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(InputComponent))
	{
		if (MouseMove)
		{
			EIC->BindAction(MouseMove,ETriggerEvent::Triggered,this,&ACPP_PlayerController::HandleMouseMove);
		}
		if (MouseZoom)
		{
			EIC->BindAction(MouseZoom, ETriggerEvent::Triggered,
							this, &ACPP_PlayerController::HandleMouseZoom);
		}

	}
	
}

void ACPP_PlayerController::HandleMouseMove(const FInputActionValue& Value)
{
	// if (IsInputKeyDown(EKeys::LeftMouseButton))
	// {
	// 	UE_LOG(LogTemp,Warning,TEXT("I'm getting the mouse input and left click!"));
	// 	GetMouseFunctionComp()->OrbitFromMouse(Value.Get<FVector2D>());
	// }


	const FVector2D MouseDelta = Value.Get<FVector2D>();

	if (UCPP_MouseFunctionComp* MouseComp = GetMouseFunctionComp())
	{
		if (IsInputKeyDown(EKeys::RightMouseButton))
		{
			// Rotate / orbit
			MouseComp->OrbitFromMouse(MouseDelta);
		}
		else if (IsInputKeyDown(EKeys::LeftMouseButton))
		{
			// Pan / relocate camera
			MouseComp->PanFromMouse(MouseDelta);
		}
	}

}


void ACPP_PlayerController::HandleMouseZoom(const FInputActionValue& Value)
{
	const float ZoomInput = Value.Get<float>();

	if (UCPP_MouseFunctionComp* MouseComp = GetMouseFunctionComp())
	{
		MouseComp->ZoomCamera(ZoomInput);
	}
}


UCPP_MouseFunctionComp* ACPP_PlayerController::GetMouseFunctionComp()
{
	APawn* CurrentPawn = GetPawn();
	if (!CurrentPawn)
	{
		return nullptr;
	}

	return CurrentPawn->FindComponentByClass<UCPP_MouseFunctionComp>();
}
