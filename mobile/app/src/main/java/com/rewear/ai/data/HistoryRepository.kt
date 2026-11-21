package com.rewear.ai.data

import kotlinx.coroutines.flow.Flow

class HistoryRepository(private val historyDao: HistoryDao) {
    val allHistory: Flow<List<HistoryEntity>> = historyDao.getAllHistory()

    suspend fun getById(id: Long): HistoryEntity? {
        return historyDao.getHistoryById(id)
    }

    suspend fun insert(entity: HistoryEntity) {
        historyDao.insertHistory(entity)
    }

    suspend fun deleteById(id: Long) {
        historyDao.deleteHistoryById(id)
    }

    suspend fun clearAll() {
        historyDao.clearAllHistory()
    }
}
