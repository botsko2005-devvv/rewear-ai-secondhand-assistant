package com.rewear.ai

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.google.gson.Gson
import com.google.gson.JsonParseException
import com.google.gson.stream.MalformedJsonException
import com.rewear.ai.data.AppDatabase
import com.rewear.ai.data.HistoryEntity
import com.rewear.ai.data.HistoryRepository
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import java.io.IOException
import java.net.SocketTimeoutException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class ListingViewModel(application: Application) : AndroidViewModel(application) {

    private val repository: HistoryRepository by lazy {
        val dao = AppDatabase.getDatabase(application).historyDao()
        HistoryRepository(dao)
    }

    val historyList: StateFlow<List<HistoryEntity>> = repository.allHistory
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    var uiState by mutableStateOf<UiState>(UiState.Idle)
        private set

    fun generate(description: String, condition: String, size: String, platform: String = "OLX") {
        val text = description.trim()

        // Клієнтська валідація: на backend такий запит не йде
        if (text.isEmpty()) {
            uiState = UiState.Error("Введіть опис речі.")
            return
        }
        if (text.length > 500) {
            uiState = UiState.Error("Опис задовгий: максимум 500 символів.")
            return
        }

        uiState = UiState.Loading
        viewModelScope.launch {
            uiState = try {
                val request = ListingRequestDto(
                    description = text,
                    condition = condition,
                    size = size.trim().ifEmpty { null },
                    platform = platform
                )
                val response = ApiClient.api.createListing(request)
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body == null) {
                        UiState.Error("Сервер повернув порожню відповідь.")
                    } else if (body.status == "ok") {
                        val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
                        val entity = HistoryEntity(
                            createdAt = dateFormat.format(Date()),
                            timestamp = System.currentTimeMillis(),
                            status = "готово",
                            description = text,
                            condition = condition,
                            size = size.trim(),
                            platform = platform,
                            category = body.category ?: "",
                            title = body.title ?: "",
                            resultDescription = body.description ?: "",
                            priceMin = body.priceMin ?: 0,
                            priceMax = body.priceMax ?: 0,
                            currency = body.currency ?: "UAH",
                            confidence = body.confidence ?: 0.0
                        )
                        repository.insert(entity)
                        mapResponse(body)
                    } else {
                        mapResponse(body)
                    }
                } else {
                    UiState.Error(parseError(response.errorBody()?.string(), response.code()))
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: SocketTimeoutException) {
                UiState.Error("Сервер не відповів вчасно. Спробуйте ще раз.")
            } catch (e: JsonParseException) {
                UiState.Error("Сервер повернув некоректну відповідь.")
            } catch (e: MalformedJsonException) {
                UiState.Error("Сервер повернув некоректну відповідь.")
            } catch (e: IOException) {
                UiState.Error("Немає зв'язку із сервером. Перевірте, що backend запущено, і спробуйте ще раз.")
            } catch (e: Exception) {
                UiState.Error("Сталася невідома помилка. Спробуйте ще раз.")
            }
        }
    }

    fun deleteHistoryItem(id: Long) {
        viewModelScope.launch {
            repository.deleteById(id)
        }
    }

    fun clearAllHistory() {
        viewModelScope.launch {
            repository.clearAll()
        }
    }

    // DTO (JSON) -> внутрішня модель
    private fun mapResponse(dto: ListingResponseDto): UiState {
        if (dto.status == "low_confidence") {
            return UiState.NoResult(dto.hint ?: "Уточніть опис речі.")
        }
        val category = dto.category
        val title = dto.title
        val description = dto.description
        val min = dto.priceMin
        val max = dto.priceMax
        if (dto.status != "ok" || category == null || title == null ||
            description == null || min == null || max == null
        ) {
            return UiState.Error("Сервер повернув неповні дані.")
        }
        return UiState.Success(
            Listing(
                category = category,
                priceMin = min,
                priceMax = max,
                currency = dto.currency ?: "UAH",
                title = title,
                description = description,
                confidence = dto.confidence ?: 0.0
            )
        )
    }

    private fun parseError(body: String?, code: Int): String {
        return try {
            Gson().fromJson(body, ErrorDto::class.java)?.message
        } catch (e: Exception) {
            null
        } ?: "Помилка сервера (код $code)."
    }

    fun reset() {
        uiState = UiState.Idle
    }
}
