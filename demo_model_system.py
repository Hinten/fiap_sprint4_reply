#!/usr/bin/env python3
"""
Script de demonstração do sistema de gerenciamento de modelos.

Este script demonstra:
1. Como salvar modelos no registry
2. Como listar modelos salvos
3. Como carregar e usar modelos para previsão
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

import numpy as np
from src.utils.model_store import (
    save_model,
    list_models,
    load_model,
    get_models_summary,
    delete_model
)


class DemoClassifier:
    """Classificador de demonstração."""
    
    def __init__(self, name="DemoModel", threshold=15.0):
        self.name = name
        self.threshold = threshold
        self.classes_ = [0, 1]
    
    def predict(self, X):
        """Predição baseada na média dos features."""
        predictions = []
        for row in X:
            mean_val = np.mean(row)
            predictions.append(1 if mean_val > self.threshold else 0)
        return np.array(predictions)
    
    def predict_proba(self, X):
        """Retorna probabilidades."""
        probas = []
        for row in X:
            mean_val = np.mean(row)
            if mean_val > self.threshold:
                distance = min((mean_val - self.threshold) / max(self.threshold, 1), 1)
                prob_1 = 0.5 + distance * 0.5
                prob_0 = 1 - prob_1
            else:
                distance = min((self.threshold - mean_val) / max(self.threshold, 1), 1)
                prob_0 = 0.5 + distance * 0.5
                prob_1 = 1 - prob_0
            probas.append([prob_0, prob_1])
        return np.array(probas)


def print_header(text):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def demo_save_models():
    """Demonstra como salvar modelos."""
    print_header("DEMONSTRAÇÃO: Salvando Modelos")
    
    models_to_save = [
        ("random_forest_demo", 12.0, {
            "accuracy": 0.92,
            "precision": 0.90,
            "recall": 0.89,
            "model_type": "RandomForest",
            "description": "Modelo Random Forest otimizado"
        }),
        ("logistic_regression_demo", 15.0, {
            "accuracy": 0.88,
            "precision": 0.87,
            "recall": 0.86,
            "model_type": "LogisticRegression",
            "description": "Modelo de Regressão Logística"
        }),
        ("gradient_boosting_demo", 10.0, {
            "accuracy": 0.94,
            "precision": 0.93,
            "recall": 0.92,
            "model_type": "GradientBoosting",
            "description": "Modelo Gradient Boosting com melhor performance"
        }),
    ]
    
    for name, threshold, metadata in models_to_save:
        try:
            model = DemoClassifier(name=name, threshold=threshold)
            save_model(model, name, metadata)
            print(f"✅ Modelo '{name}' salvo com sucesso!")
            print(f"   Tipo: {metadata['model_type']}")
            print(f"   Accuracy: {metadata['accuracy']:.2%}")
            print()
        except ValueError as e:
            print(f"⚠️  Modelo '{name}' já existe - pulando")
            print()


def demo_list_models():
    """Demonstra como listar modelos."""
    print_header("DEMONSTRAÇÃO: Listando Modelos Salvos")
    
    registry = list_models()
    
    if not registry:
        print("⚠️  Nenhum modelo encontrado no registry.")
        return
    
    print(f"📚 Total de modelos salvos: {len(registry)}\n")
    
    summary = get_models_summary()
    
    # Ordena por accuracy
    summary_sorted = sorted(summary, key=lambda x: x.get('accuracy', 0), reverse=True)
    
    for idx, model_info in enumerate(summary_sorted, 1):
        print(f"{idx}. {model_info['name']}")
        print(f"   Tipo: {model_info.get('model_type', 'N/A')}")
        print(f"   Accuracy: {model_info.get('accuracy', 0):.2%}")
        print(f"   Salvo em: {model_info.get('saved_at', 'N/A')}")
        if 'description' in model_info:
            print(f"   Descrição: {model_info['description']}")
        print()


def demo_load_and_predict():
    """Demonstra como carregar e usar modelos."""
    print_header("DEMONSTRAÇÃO: Carregando e Usando Modelos")
    
    registry = list_models()
    
    if not registry:
        print("⚠️  Nenhum modelo disponível para carregar.")
        return
    
    # Pega o primeiro modelo disponível
    model_name = list(registry.keys())[0]
    
    print(f"🔄 Carregando modelo: {model_name}")
    
    try:
        model = load_model(model_name)
        print(f"✅ Modelo carregado com sucesso!\n")
        
        # Dados de teste (simula leituras de sensores)
        test_cases = [
            {
                "name": "Operação Normal",
                "data": np.array([[15.0, 14.0, 0.5]]),  # Lux, Temp, Vibração
                "description": "Valores normais de operação"
            },
            {
                "name": "Alta Vibração",
                "data": np.array([[50.0, 80.0, 100.0]]),
                "description": "Vibração elevada detectada"
            },
            {
                "name": "Baixa Temperatura",
                "data": np.array([[10.0, 5.0, 1.0]]),
                "description": "Temperatura abaixo do normal"
            },
        ]
        
        print("🔮 Fazendo Previsões:\n")
        
        for test in test_cases:
            print(f"📊 Cenário: {test['name']}")
            print(f"   {test['description']}")
            print(f"   Lux={test['data'][0][0]:.1f}, Temp={test['data'][0][1]:.1f}°C, Vibração={test['data'][0][2]:.1f}")
            
            prediction = model.predict(test['data'])
            probabilities = model.predict_proba(test['data'])
            
            if prediction[0] == 1:
                resultado = "⚠️  MANUTENÇÃO NECESSÁRIA"
            else:
                resultado = "✅ SEM NECESSIDADE DE MANUTENÇÃO"
            
            print(f"   Resultado: {resultado}")
            print(f"   Probabilidades: Sem Manutenção={probabilities[0][0]:.2%}, "
                  f"Com Manutenção={probabilities[0][1]:.2%}")
            print()
            
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")


def demo_cleanup():
    """Remove modelos de demonstração."""
    print_header("LIMPEZA: Removendo Modelos de Demonstração")
    
    demo_models = [
        "random_forest_demo",
        "logistic_regression_demo",
        "gradient_boosting_demo"
    ]
    
    for model_name in demo_models:
        try:
            delete_model(model_name)
            print(f"🗑️  Modelo '{model_name}' removido")
        except FileNotFoundError:
            print(f"⚠️  Modelo '{model_name}' não encontrado")
    
    print()


def main():
    """Executa demonstração completa."""
    print("\n" + "🤖 " * 35)
    print("  SISTEMA DE GERENCIAMENTO DE MODELOS - DEMONSTRAÇÃO")
    print("🤖 " * 35)
    
    # 1. Salvar modelos
    demo_save_models()
    
    # 2. Listar modelos
    demo_list_models()
    
    # 3. Carregar e prever
    demo_load_and_predict()
    
    # 4. Cleanup (opcional - descomente para remover)
    # demo_cleanup()
    # demo_list_models()
    
    print_header("DEMONSTRAÇÃO CONCLUÍDA")
    print("✨ O sistema está pronto para uso!\n")
    print("📖 Próximos passos:")
    print("   1. Execute o dashboard: streamlit run main_dash.py")
    print("   2. Navegue até a página 'Train Model'")
    print("   3. Treine modelos e salve os top 5")
    print("   4. Use a página 'Classificador Manual' para fazer previsões\n")


if __name__ == "__main__":
    main()
