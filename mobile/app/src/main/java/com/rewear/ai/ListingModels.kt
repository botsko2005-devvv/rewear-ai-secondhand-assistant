package com.rewear.ai

import com.google.gson.annotations.SerializedName

// DTO: так виглядає JSON
data class ListingRequestDto(
    val description: String,
    val condition: String,
    val size: String? = null
)

data class ListingResponseDto(
    val status: String?,
    val category: String?,
    val condition: String?,
    @SerializedName("price_min") val priceMin: Int?,
    @SerializedName("price_max") val priceMax: Int?,
    val currency: String?,
    val title: String?,
    val description: String?,
    val hint: String?,
    val confidence: Double?
)

data class ErrorDto(
    val error: String?,
    val message: String?
)

// Внутрішня модель, з якою працює інтерфейс
data class Listing(
    val category: String,
    val priceMin: Int,
    val priceMax: Int,
    val currency: String,
    val title: String,
    val description: String,
    val confidence: Double
)

// Стани екрана
sealed class UiState {
    object Idle : UiState()
    object Loading : UiState()
    data class Success(val listing: Listing) : UiState()
    data class NoResult(val hint: String) : UiState()
    data class Error(val message: String) : UiState()
}