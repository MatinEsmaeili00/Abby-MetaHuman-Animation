// Fill out your copyright notice in the Description page of Project Settings.


#include "AnimationTimelineComp.h"



// Sets default values for this component's properties
UAnimationTimelineComp::UAnimationTimelineComp():NormalizedTime{.0f},bIsPlaying{false},bReverse{false},PlaySpeed{1.f}
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;

	// ...
}


// Called when the game starts
void UAnimationTimelineComp::BeginPlay()
{
	Super::BeginPlay();

	// ...


	// Auto–find mesh if you didn’t assign it in editor
	if (!SkeletalMesh)
	{
		SkeletalMesh = GetOwner()->FindComponentByClass<USkeletalMeshComponent>();
	}

	if (SkeletalMesh && AnimationSequence)
	{
		// // Make sure we’re using the single-node mode
		// SkeletalMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
		// SkeletalMesh->SetAnimation(AnimationSequence);
		//
		// // Stop auto playing, we’ll drive time ourselves
		// SkeletalMesh->Stop();

		AnimLength = AnimationSequence->GetPlayLength();

		SingleNodeInstance = Cast<UAnimSingleNodeInstance>(SkeletalMesh->GetAnimInstance());
	}

	
	
}


// Called every frame
void UAnimationTimelineComp::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// ...


	if (!bIsPlaying || !SingleNodeInstance || AnimLength <= 0.f)
		return;

	const float Direction = bReverse ? -1.f : 1.f;

	// convert seconds to normalized units  (1 real sec → 1/AnimLength of the clip)
	const float DeltaNormalized = Direction * PlaySpeed * DeltaTime / AnimLength;

	NormalizedTime = FMath::Clamp(NormalizedTime + DeltaNormalized, 0.f, 1.f);

	UpdateAnimPosition( NormalizedTime,SingleNodeInstance, AnimLength);

	
}

void UAnimationTimelineComp::UpdateAnimPosition(float InNormalizedTime,UAnimSingleNodeInstance* InSingleNodeInstance,float InAnimLength)
{
	if (!InSingleNodeInstance || InAnimLength <= 0.f) return;

	const float PositionSeconds = InNormalizedTime * InAnimLength;

	// false = don’t fire notifies, you can change if you want them
	InSingleNodeInstance->SetPosition(PositionSeconds, false);
	InSingleNodeInstance->SetPlaying(false); // we’re manually driving position
}

void UAnimationTimelineComp::PlayForward()
{
	bReverse = false;
	bIsPlaying = true;
}

void UAnimationTimelineComp::PlayReverse()
{
	bReverse = true;
	bIsPlaying = true;
}

void UAnimationTimelineComp::Pause()
{
	bIsPlaying = false;
}

void UAnimationTimelineComp::SetNormalizedTime(float InAlpha)
{
	NormalizedTime = FMath::Clamp(InAlpha, 0.f, 1.f);
	UpdateAnimPosition(NormalizedTime,SingleNodeInstance, AnimLength); // jump immediately
}


