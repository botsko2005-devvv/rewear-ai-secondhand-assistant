package com.rewear.ai.data

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "listing_history")
data class HistoryEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val createdAt: String,
    val timestamp: Long,
    val status: String = "готово",
    val description: String,
    val condition: String,
    val size: String,
    val platform: String,
    val category: String,
    val title: String,
    val resultDescription: String,
    val priceMin: Int,
    val priceMax: Int,
    val currency: String,
    val confidence: Double
)
