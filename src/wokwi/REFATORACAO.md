# Refatoração do Sistema de Display - LCD e Serial

## 📋 Índice
1. [O que foi feito](#o-que-foi-feito)
2. [Como usar (ELI5)](#como-usar-eli5)
3. [Como funciona por trás](#como-funciona-por-trás)
4. [Bugs encontrados e correções](#bugs-encontrados-e-correções)
5. [Notas e recomendações](#notas-e-recomendações)

---

## O que foi feito

Esta refatoração transformou o código do ESP32 para suportar diferentes configurações de LCD (20x4, 16x2 ou nenhum LCD), com gerenciamento centralizado de todas as saídas de texto.

### Mudanças principais:

1. **Criação de 3 novos arquivos:**
   - `config.h` - Arquivo de configuração onde você escolhe o tipo de LCD
   - `display_manager.h` - Declarações das funções de display
   - `display_manager.cpp` - Implementação do gerenciador de display

2. **Refatoração completa do `sketch.cpp`:**
   - Todos os `lcd.print()` foram removidos
   - Todos os `Serial.print()` foram organizados
   - Agora usamos funções centralizadas: `displayPrint()`, `displayPrintAt()`, `displayPrintf()`, etc.

3. **Funcionalidades novas:**
   - Suporte para LCD 20x4 (padrão)
   - Suporte para LCD 16x2 com paginação automática
   - Modo sem LCD (apenas Serial Monitor)
   - Sincronização automática LCD ↔ Serial
   - Truncamento automático de mensagens longas
   - Paginação automática quando o conteúdo não cabe no display

---

## Como usar (ELI5)

### Passo 1: Escolher o tipo de LCD

Abra o arquivo `src/wokwi/src/config.h` e procure esta linha:

```cpp
const LcdType SELECTED_LCD = LCD_20x4;
```

Você pode mudar para uma destas opções:

- `LCD_20x4` - Para LCD de 20 colunas e 4 linhas (padrão)
- `LCD_16x2` - Para LCD de 16 colunas e 2 linhas
- `LCD_NONE` - Se não tiver LCD (só vai aparecer no Serial Monitor)

### Passo 2: Compilar e fazer upload

Depois de escolher, compile o código normalmente e faça upload para o ESP32.

### Passo 3: Ver as mensagens

- **Se você escolheu um LCD:** As mensagens aparecem no LCD E no Serial Monitor
- **Se você escolheu LCD_NONE:** Todas as mensagens aparecem APENAS no Serial Monitor
- **Se você tem LCD 16x2:** Quando houver mais de 2 linhas de informação, o display vai:
  1. Mostrar as 2 primeiras linhas
  2. Esperar 2 segundos
  3. Limpar a tela
  4. Mostrar as próximas linhas

### Exemplo prático:

**Antes (código antigo):**
```cpp
lcd.setCursor(0, 0);
lcd.print("Temp: ");
lcd.print(tempC, 1);
lcd.print(" C");
Serial.print("Temperatura: ");
Serial.print(tempC, 1);
Serial.println(" C");
```

**Depois (código novo):**
```cpp
char buffer[32];
snprintf(buffer, sizeof(buffer), "Temp: %.1f C", tempC);
displayPrintAt(0, 0, buffer);
```

Muito mais simples! E automaticamente aparece tanto no LCD quanto no Serial.

---

## Como funciona por trás

### Arquitetura

```
┌─────────────────┐
│   sketch.cpp    │  ← Código principal
│                 │
│  displayPrint() │  ← Chama funções do display manager
└────────┬────────┘
         │
         ▼
┌────────────────────┐
│ display_manager.cpp│  ← Gerenciador centralizado
│                    │
│ • Detecta LCD      │
│ • Sincroniza LCD/  │
│   Serial           │
│ • Pagina conteúdo  │
│ • Trunca textos    │
└─────┬──────────────┘
      │
      ├──────────────┐
      ▼              ▼
┌──────────┐  ┌──────────┐
│   LCD    │  │  Serial  │
│  20x4    │  │ Monitor  │
│  16x2    │  │          │
│  ou NONE │  │          │
└──────────┘  └──────────┘
```

### Funções principais:

1. **`displayInit()`** - Inicializa LCD e Serial baseado em `config.h`
2. **`displayPrint(msg)`** - Imprime uma mensagem simples
3. **`displayPrintAt(col, row, msg)`** - Imprime em posição específica
4. **`displayPrintLines(lines[], count)`** - Imprime múltiplas linhas com paginação
5. **`displayClear()`** - Limpa o display
6. **`displayPrintf(col, row, format, ...)`** - Imprime com formatação (tipo printf)

### Lógica de paginação (LCD 16x2):

Quando você tenta imprimir na linha 2 ou 3 de um LCD 16x2:

```cpp
displayPrintAt(0, 2, "Accelerometer:");  // Linha 2 não existe em 16x2!
displayPrintAt(0, 3, "x:1.2 y:0.5");     // Linha 3 não existe em 16x2!
```

O sistema faz:
1. Detecta que row >= 2 (fora do alcance do 16x2)
2. Limpa o LCD
3. Espera `DISPLAY_PAGE_DELAY_MS` (2 segundos)
4. Mapeia as linhas 2→0, 3→1
5. Mostra o conteúdo na "próxima página"

---

## Bugs encontrados e correções

### 🐛 Bug 1: Comentário contradiz implementação
**Localização:** Linha 12-13 do `sketch.cpp` original

**Problema:**
```cpp
// Inicializa o LCD I2C no endereço 0x27 com tamanho 16x2
LiquidCrystal_I2C lcd(0x27, 20, 4);  // ← Mas na verdade usa 20x4!
```

**Impacto:** Confusão sobre qual LCD usar. Se alguém conectasse um LCD 16x2 real, o código tentaria escrever em linhas que não existem (linhas 2 e 3), causando comportamento indefinido.

**Correção:** Criamos `config.h` com seleção explícita do tipo de LCD. Agora o usuário escolhe claramente qual LCD tem.

---

### 🐛 Bug 2: Uso excessivo de String() dinâmico
**Localização:** Múltiplos lugares no código original

**Problema:**
```cpp
Serial.print(" (Lux: " + String(lux) + ") |");
print_lcd_and_serial("Chip ID: " + String(chipidStr));
```

**Impacto:** A classe `String` do Arduino aloca memória dinamicamente, causando:
- Fragmentação de heap
- Possíveis crashes em execuções longas
- Consumo desnecessário de RAM

**Correção:** Substituímos todos os usos de `String()` por `snprintf()` com buffers char estáticos:
```cpp
char buffer[64];
snprintf(buffer, sizeof(buffer), "Chip ID: %s", chipidStr);
displayPrint(buffer);
```

---

### 🐛 Bug 3: Prints não sincronizados entre LCD e Serial
**Localização:** Várias partes do código

**Problema:**
```cpp
// Às vezes só imprimia no LCD:
lcd.setCursor(0, 2);
lcd.print("Accelerometer:");

// Às vezes só no Serial:
Serial.print(" X:");
```

**Impacto:** Informações inconsistentes entre o que aparece no LCD e no Serial Monitor. Dificulta debug e monitoramento.

**Correção:** Todas as funções do `display_manager` automaticamente enviam para LCD E Serial. Impossível desincronizar agora.

---

### 🐛 Bug 4: Tentativa de escrever em linhas inexistentes
**Localização:** Loop principal, linhas 285-294 do original

**Problema:**
```cpp
lcd.setCursor(0, 2);  // OK para LCD 20x4
lcd.print("Accelerometer:");
lcd.setCursor(0, 3);  // OK para LCD 20x4
lcd.print("x:...");   // Mas se fosse 16x2, linhas 2 e 3 não existem!
```

**Impacto:** Em um LCD 16x2 real, isso causa comportamento indefinido (pode sobrescrever linha 0 ou 1, ou mostrar caracteres aleatórios).

**Correção:** O `display_manager` detecta quando `row >= lcdRows` e:
- Para LCD 16x2: Implementa paginação automática
- Trunca ou mapeia a linha para dentro do alcance válido

---

### 🐛 Bug 5: Falta de uso de F() macro para strings constantes
**Localização:** Todo o código

**Problema:**
```cpp
Serial.println("WiFi desconectado, impossível fazer requisição!");
```

**Impacto:** Strings literais ocupam RAM preciosa do ESP32. O ESP32 tem RAM limitada (~320KB), e cada string consome espaço.

**Correção:** Usamos `F()` macro para mover strings para memória Flash:
```cpp
Serial.println(F("WiFi desconectado, impossível fazer requisição!"));
```

Economia estimada: ~500-800 bytes de RAM.

---

### 🐛 Bug 6: Função `iniciar_lcd()` não reutilizável
**Localização:** Linhas 15-20 do original

**Problema:**
```cpp
void iniciar_lcd() {
  lcd.begin(20, 4);  // Hardcoded!
  lcd.backlight();
  lcd.print("LCD OK!");
  delay(1000);
}
```

**Impacto:** Impossível adaptar para outros tamanhos de LCD sem modificar código-fonte.

**Correção:** `displayInit()` detecta automaticamente as dimensões baseado em `SELECTED_LCD` do `config.h`.

---

### 🐛 Bug 7: Comentário incorreto sobre conversão
**Localização:** Linha 211 do original

**Problema:**
```cpp
// Converte para g (gravidade da Terra)  ← ERRADO!
float gx = gx_raw / 131.0;  // Na verdade converte para graus/segundo
```

**Impacto:** Confusão conceitual. Giroscópios medem rotação (°/s), não aceleração (g).

**Correção:** Corrigimos o comentário:
```cpp
// Converte para graus/segundo
float gx = gx_raw / 131.0;
```

---

## Notas e recomendações

### ✅ Boas práticas implementadas:

1. **Separação de responsabilidades:**
   - `config.h` = configuração
   - `display_manager.*` = lógica de exibição
   - `sketch.cpp` = lógica de aplicação

2. **Uso de F() macro:** Economiza RAM movendo strings para Flash

3. **Buffers char estáticos:** Evita fragmentação de heap

4. **Include guards:** Todos os `.h` têm `#ifndef`/`#define`

5. **Constantes configuráveis:** `DISPLAY_PAGE_DELAY_MS` pode ser ajustado

### 🔧 Como ajustar o tempo de paginação:

Se o delay de 2 segundos entre páginas for muito longo/curto, edite `config.h`:

```cpp
const int DISPLAY_PAGE_DELAY_MS = 2000;  // Mude este valor
```

### 🧪 Testes sugeridos:

1. **Teste com LCD 20x4:**
   ```cpp
   // config.h
   const LcdType SELECTED_LCD = LCD_20x4;
   ```
   Compilar, fazer upload, verificar se todas as 4 linhas aparecem.

2. **Teste com LCD 16x2:**
   ```cpp
   const LcdType SELECTED_LCD = LCD_16x2;
   ```
   Verificar se a paginação funciona (2 linhas → espera → próximas 2 linhas).

3. **Teste sem LCD:**
   ```cpp
   const LcdType SELECTED_LCD = LCD_NONE;
   ```
   Abrir Serial Monitor, verificar se todas as mensagens aparecem corretamente.

### 📝 Manutenção futura:

**Para adicionar uma nova mensagem no código:**

```cpp
// Opção 1: Mensagem simples
displayPrint("Minha mensagem");

// Opção 2: Em posição específica
displayPrintAt(0, 1, "Linha 2");

// Opção 3: Com formatação
displayPrintf(0, 0, "Valor: %.2f", minhaVariavel);

// Opção 4: Múltiplas linhas
const char* linhas[] = {
  "Linha 1",
  "Linha 2",
  "Linha 3"
};
displayPrintLines(linhas, 3);
```

**NUNCA MAIS USE:**
- ❌ `lcd.print()` diretamente
- ❌ `Serial.print()` sem também mostrar no LCD (se aplicável)
- ❌ `String()` para concatenar (use `snprintf()`)

---

## 🎯 Resumo

**Antes:**
- Código espalhado com lcd.print() e Serial.print() misturados
- Hardcoded para LCD 20x4
- Bugs de sincronização e memória
- Difícil de adaptar para outros LCDs

**Depois:**
- Código limpo com funções centralizadas
- Suporta 20x4, 16x2 ou nenhum LCD
- Sincronização automática LCD ↔ Serial
- Paginação automática para displays menores
- Código mais fácil de manter e estender

---

## 📚 Referências

- [LiquidCrystal_I2C Library Documentation](https://github.com/johnrickman/LiquidCrystal_I2C)
- [Arduino String vs char array](https://www.arduino.cc/reference/en/language/variables/data-types/stringobject/)
- [F() macro documentation](https://www.arduino.cc/reference/en/language/variables/utilities/progmem/)
- [ESP32 Memory Management Best Practices](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/performance/ram-usage.html)

---

**Versão:** 1.0  
**Data:** Outubro 2025  
**Autor:** Refatoração automatizada para FIAP Sprint 4
