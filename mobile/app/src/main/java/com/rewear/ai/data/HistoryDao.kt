package com.rewear.ai.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface HistoryDao {
    @Query("SELECT * FROM listing_history ORDER BY timestamp DESC")
    fun getAllHistory(): Flow<List<HistoryEntity>>

    @Query("SELECT * FROM listing_history WHERE id = :id")
    suspend fun getHistoryById(id: Long): HistoryEntity?

    @Insert
    suspend fun insertHistory(entity: HistoryEntity)

    @Query("DELETE FROM listing_history WHERE id = :id")
    suspend fun deleteHistoryById(id: Long)

    @Query("DELETE FROM listing_history")
    suspend fun clearAllHistory()
}
