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
import com.rewear.ai.ui.theme.ReWearAITheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ReWearAITheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    ListingScreen()
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

@Composable
fun ListingScreen(vm: ListingViewModel = viewModel()) {
    var description by rememberSaveable { mutableStateOf("") }
    var condition by rememberSaveable { mutableStateOf("good") }
    var size by rememberSaveable { mutableStateOf("") }

    val state = vm.uiState

    Column(
        modifier = Modifier
            .fillMaxSize()
            .statusBarsPadding()
            .navigationBarsPadding()
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
            onClick = { vm.generate(description, condition, size) },
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
                    OutlinedButton(onClick = { vm.generate(description, condition, size) }) {
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