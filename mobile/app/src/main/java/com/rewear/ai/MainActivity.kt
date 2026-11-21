package com.rewear.ai

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.selection.selectable
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.rewear.ai.data.HistoryEntity
import com.rewear.ai.ui.theme.ReWearAITheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ReWearAITheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    MainScreen()
                }
            }
        }
    }
}

private val CONDITIONS = listOf(
    "new" to "Новий",
    "excellent" to "Відмінний",
    "good" to "Добрий",
    "fair" to "Задовільний"
)

private val PLATFORMS = listOf(
    "OLX" to "OLX",
    "eBay" to "eBay",
    "Grailed" to "Grailed"
)

@Composable
fun MainScreen(vm: ListingViewModel = viewModel()) {
    var selectedTab by rememberSaveable { mutableStateOf(0) }
    val history by vm.historyList.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .statusBarsPadding()
            .navigationBarsPadding()
    ) {
        PrimaryTabRow(selectedTabIndex = selectedTab) {
            Tab(
                selected = selectedTab == 0,
                onClick = { selectedTab = 0 },
                text = { Text("Генератор") }
            )
            Tab(
                selected = selectedTab == 1,
                onClick = { selectedTab = 1 },
                text = { Text("Історія (${history.size})") }
            )
        }

        when (selectedTab) {
            0 -> ListingScreen(vm = vm)
            1 -> HistoryScreen(history = history, vm = vm)
        }
    }
}

@Composable
fun ListingScreen(vm: ListingViewModel) {
    var description by rememberSaveable { mutableStateOf("") }
    var condition by rememberSaveable { mutableStateOf("good") }
    var size by rememberSaveable { mutableStateOf("") }
    var platform by rememberSaveable { mutableStateOf("OLX") }

    val state = vm.uiState

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text("ReWear AI", style = MaterialTheme.typography.headlineMedium)
        Text(
            "Опишіть річ — отримайте категорію, ціну та готовий текст оголошення.",
            style = MaterialTheme.typography.bodyMedium
        )

        OutlinedTextField(
            value = description,
            onValueChange = { description = it },
            label = { Text("Опис речі") },
            placeholder = { Text("Куртка Zara, носив один сезон, є дрібна потертість") },
            supportingText = { Text("${description.length}/500") },
            isError = description.length > 500,
            minLines = 3,
            modifier = Modifier.fillMaxWidth()
        )

        Text("Майданчик публікації", style = MaterialTheme.typography.titleSmall)
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            PLATFORMS.forEach { (value, label) ->
                FilterChip(
                    selected = platform == value,
                    onClick = { platform = value },
                    label = { Text(label) }
                )
            }
        }

        Text("Стан", style = MaterialTheme.typography.titleSmall)
        CONDITIONS.forEach { (value, label) ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .selectable(
                        selected = condition == value,
                        onClick = { condition = value },
                        role = Role.RadioButton
                    ),
                verticalAlignment = Alignment.CenterVertically
            ) {
                RadioButton(selected = condition == value, onClick = null)
                Text(label, modifier = Modifier.padding(start = 8.dp))
            }
        }

        OutlinedTextField(
            value = size,
            onValueChange = { size = it },
            label = { Text("Розмір (необов'язково)") },
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        Button(
            onClick = { vm.generate(description, condition, size, platform) },
            enabled = state !is UiState.Loading,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Згенерувати оголошення")
        }

        when (state) {
            is UiState.Idle -> Text("Введіть опис і натисніть кнопку.")

            is UiState.Loading -> Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                CircularProgressIndicator()
                Text("Аналізуємо опис...")
            }

            is UiState.Success -> ResultCard(state.listing)

            is UiState.NoResult -> Card(modifier = Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Результату немає", style = MaterialTheme.typography.titleMedium)
                    Text(state.hint)
                }
            }

            is UiState.Error -> Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.errorContainer
                )
            ) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Помилка", style = MaterialTheme.typography.titleMedium)
                    Text(state.message)
                    OutlinedButton(onClick = { vm.generate(description, condition, size, platform) }) {
                        Text("Повторити")
                    }
                }
            }
        }
    }
}

@Composable
fun ResultCard(listing: Listing) {
    val context = LocalContext.current
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Категорія: ${listing.category}", style = MaterialTheme.typography.titleMedium)
            Text("Ціна: ${listing.priceMin}–${listing.priceMax} грн")
            HorizontalDivider()
            Text("Заголовок", style = MaterialTheme.typography.labelMedium)
            Text(listing.title, style = MaterialTheme.typography.titleSmall)
            Text("Опис", style = MaterialTheme.typography.labelMedium)
            Text(listing.description)
            Text(
                "Впевненість AI: ${(listing.confidence * 100).toInt()}%",
                style = MaterialTheme.typography.bodySmall
            )
            Button(onClick = {
                val cm = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                cm.setPrimaryClip(
                    ClipData.newPlainText("listing", "${listing.title}\n\n${listing.description}")
                )
                Toast.makeText(context, "Скопійовано", Toast.LENGTH_SHORT).show()
            }) {
                Text("Копіювати оголошення")
            }
        }
    }
}

@Composable
fun HistoryScreen(history: List<HistoryEntity>, vm: ListingViewModel) {
    var selectedItem by remember { mutableStateOf<HistoryEntity?>(null) }
    var showClearDialog by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Історія генерацій", style = MaterialTheme.typography.headlineSmall)
            if (history.isNotEmpty()) {
                OutlinedButton(onClick = { showClearDialog = true }) {
                    Text("Очистити історію")
                }
            }
        }

        if (history.isEmpty()) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(32.dp),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    "Історія порожня. Згенеруйте перше оголошення, щоб зберегти результат.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(history, key = { it.id }) { item ->
                    HistoryItemCard(item = item, onClick = { selectedItem = item })
                }
            }
        }
    }

    selectedItem?.let { item ->
        HistoryDetailDialog(
            item = item,
            onDismiss = { selectedItem = null },
            onDelete = {
                vm.deleteHistoryItem(item.id)
                selectedItem = null
            }
        )
    }

    if (showClearDialog) {
        AlertDialog(
            onDismissRequest = { showClearDialog = false },
            title = { Text("Очистити історію") },
            text = { Text("Ви дійсно хочете видалити всі записи з історії?") },
            confirmButton = {
                TextButton(onClick = {
                    vm.clearAllHistory()
                    showClearDialog = false
                }) {
                    Text("Видалити все")
                }
            },
            dismissButton = {
                TextButton(onClick = { showClearDialog = false }) {
                    Text("Скасувати")
                }
            }
        )
    }
}

@Composable
fun HistoryItemCard(item: HistoryEntity, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = item.category.ifEmpty { item.title },
                    style = MaterialTheme.typography.titleMedium
                )
                Badge {
                    Text(item.status)
                }
            }
            Text(
                text = "Ціна: ${item.priceMin}–${item.priceMax} ${item.currency}",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary
            )
            Text(
                text = "Запит: ${item.description} (${item.platform})",
                style = MaterialTheme.typography.bodySmall,
                maxLines = 1
            )
            Text(
                text = item.createdAt,
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
fun HistoryDetailDialog(
    item: HistoryEntity,
    onDismiss: () -> Unit,
    onDelete: () -> Unit
) {
    val context = LocalContext.current
    var showDeleteDialog by remember { mutableStateOf(false) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(item.title.ifEmpty { "Деталі оголошення" }) },
        text = {
            Column(
                modifier = Modifier
                    .verticalScroll(rememberScrollState())
                    .fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text("Категорія: ${item.category}", style = MaterialTheme.typography.titleSmall)
                Text("Ціна: ${item.priceMin}–${item.priceMax} ${item.currency}")
                Text("Майданчик: ${item.platform} | Стан: ${item.condition}" + if (item.size.isNotEmpty()) " | Розмір: ${item.size}" else "")
                HorizontalDivider()
                Text("Текст результату:", style = MaterialTheme.typography.labelMedium)
                Text(item.resultDescription, style = MaterialTheme.typography.bodyMedium)
                HorizontalDivider()
                Text("Вихідний опис:", style = MaterialTheme.typography.labelMedium)
                Text(item.description, style = MaterialTheme.typography.bodySmall)
                Text("Дата: ${item.createdAt}", style = MaterialTheme.typography.labelSmall)
            }
        },
        confirmButton = {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                TextButton(onClick = {
                    val cm = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                    cm.setPrimaryClip(
                        ClipData.newPlainText("listing", "${item.title}\n\n${item.resultDescription}")
                    )
                    Toast.makeText(context, "Скопійовано", Toast.LENGTH_SHORT).show()
                }) {
                    Text("Копіювати")
                }
                TextButton(onClick = { showDeleteDialog = true }) {
                    Text("Видалити", color = MaterialTheme.colorScheme.error)
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Закрити")
            }
        }
    )

    if (showDeleteDialog) {
        AlertDialog(
            onDismissRequest = { showDeleteDialog = false },
            title = { Text("Видалити запис") },
            text = { Text("Ви дійсно хочете видалити цей запис з історії?") },
            confirmButton = {
                TextButton(onClick = {
                    showDeleteDialog = false
                    onDelete()
                }) {
                    Text("Видалити", color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteDialog = false }) {
                    Text("Скасувати")
                }
            }
        )
    }
}
