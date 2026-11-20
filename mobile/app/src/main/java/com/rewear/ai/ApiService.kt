package com.rewear.ai

import okhttp3.OkHttpClient
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST
import java.util.concurrent.TimeUnit

interface ApiService {
    @POST("api/v1/listing")
    suspend fun createListing(@Body body: ListingRequestDto): Response<ListingResponseDto>
}

object ApiClient {
    // Емулятор бачить комп'ютер як 10.0.2.2
    // Для фізичного телефона заміни на IP комп'ютера, напр. "http://192.168.0.15:8000/"
    const val BASE_URL = "http://127.0.0.1:8000/"

    val api: ApiService by lazy {
        val client = OkHttpClient.Builder()
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(10, TimeUnit.SECONDS)
            .build()

        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}