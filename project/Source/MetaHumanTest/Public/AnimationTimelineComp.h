// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "AnimationTimelineComp.generated.h"



UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class METAHUMANTEST_API UAnimationTimelineComp : public UActorComponent
{
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	UAnimationTimelineComp();

protected:
	// Called when the game starts
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	

	float NormalizedTime;
	bool bIsPlaying;
	bool bReverse;
	float PlaySpeed;



	UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Animation Timeline")
	USkeletalMeshComponent* SkeletalMesh;
	UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Animation Timeline")
	UAnimSequenceBase* AnimationSequence;
	

	float AnimLength = 0.f;

	UAnimSingleNodeInstance* SingleNodeInstance = nullptr;

	void UpdateAnimPosition(float InNormalizedTime,UAnimSingleNodeInstance* InSingleNodeInstance,float InAnimLength); // internal



	/** ---- Controls for UI ---- */
	UFUNCTION(BlueprintCallable, Category="MocapTimeline")
	void PlayForward();

	UFUNCTION(BlueprintCallable, Category="MocapTimeline")
	void PlayReverse();

	UFUNCTION(BlueprintCallable, Category="MocapTimeline")
	void Pause();

	UFUNCTION(BlueprintCallable, Category="MocapTimeline")
	void SetNormalizedTime(float InAlpha);

	UFUNCTION(BlueprintCallable, Category="MocapTimeline")
	float GetNormalizedTime() const { return NormalizedTime; }


	
};
