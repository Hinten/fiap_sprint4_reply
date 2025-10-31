#!/bin/bash
# ESP32 Code Structure Validation Script

echo "=== ESP32 Modular Architecture Validation ==="
echo ""

cd "$(dirname "$0")/src"

echo "1. Checking directory structure..."
echo ""

DIRS=(
    "api"
    "conexao_wifi"
    "painel_lcd"
    "sensores/sensor_ldr"
    "sensores/mpu6050"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir/ exists"
    else
        echo "  ✗ $dir/ missing"
    fi
done

echo ""
echo "2. Checking header files..."
echo ""

HEADERS=(
    "api/api.h"
    "conexao_wifi/conexao_wifi.h"
    "painel_lcd/painel_lcd.h"
    "sensores/sensor_ldr/sensor_ldr.h"
    "sensores/mpu6050/MPU6050Sensor.h"
    "config.h"
)

for header in "${HEADERS[@]}"; do
    if [ -f "$header" ]; then
        echo "  ✓ $header"
    else
        echo "  ✗ $header missing"
    fi
done

echo ""
echo "3. Checking implementation files..."
echo ""

SOURCES=(
    "conexao_wifi/conexao_wifi.cpp"
    "painel_lcd/painel_lcd.cpp"
    "sensores/sensor_ldr/sensor_ldr.cpp"
    "sensores/mpu6050/MPU6050Sensor.cpp"
    "sketch.cpp"
)

for source in "${SOURCES[@]}"; do
    if [ -f "$source" ]; then
        echo "  ✓ $source"
    else
        echo "  ✗ $source missing"
    fi
done

echo ""
echo "4. Checking for circular dependencies..."
echo ""

# Check if api.h includes conexao_wifi.h or painel_lcd.h
if grep -q "#include.*conexao_wifi.h" api/api.h 2>/dev/null; then
    echo "  ✗ api.h includes conexao_wifi.h (should use forward declaration)"
else
    echo "  ✓ api.h uses forward declaration for ConexaoWifi"
fi

if grep -q "#include.*painel_lcd.h" api/api.h 2>/dev/null; then
    echo "  ✗ api.h includes painel_lcd.h (should use forward declaration)"
else
    echo "  ✓ api.h uses forward declaration for PainelLCD"
fi

# Check if conexao_wifi.h includes painel_lcd.h
if grep -q "#include.*painel_lcd.h" conexao_wifi/conexao_wifi.h 2>/dev/null; then
    echo "  ✗ conexao_wifi.h includes painel_lcd.h (should use forward declaration)"
else
    echo "  ✓ conexao_wifi.h uses forward declaration for PainelLCD"
fi

echo ""
echo "5. Checking header guards..."
echo ""

for header in "${HEADERS[@]}"; do
    if [ -f "$header" ]; then
        GUARD=$(head -1 "$header" | grep -o "#ifndef.*")
        if [ -n "$GUARD" ]; then
            echo "  ✓ $header has header guard"
        else
            echo "  ✗ $header missing header guard"
        fi
    fi
done

echo ""
echo "6. File statistics..."
echo ""

echo "  Total source files: $(find . -name "*.cpp" | wc -l)"
echo "  Total header files: $(find . -name "*.h" | wc -l)"
echo "  Total lines of code:"

for ext in cpp h; do
    lines=$(find . -name "*.$ext" -exec cat {} \; | wc -l)
    echo "    .$ext files: $lines lines"
done

echo ""
echo "7. Module summary..."
echo ""

echo "  api/              - HTTP API client"
echo "  conexao_wifi/     - WiFi connection management"
echo "  painel_lcd/       - LCD display (supports NONE/16x2/20x4)"
echo "  sensor_ldr/       - Light sensor"
echo "  mpu6050/          - Accelerometer/Gyroscope sensor"
echo ""

echo "=== Validation Complete ==="
