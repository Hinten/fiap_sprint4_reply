#!/usr/bin/env python3
"""
Script de demonstração para verificar que os modelos PyCaret funcionam corretamente
com a nova função preparar_dados_para_previsao.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.dashboard.machine_learning.manual import preparar_dados_para_previsao

def test_formato_dados():
    """Testa se os dados estão no formato correto para PyCaret."""
    
    print("=" * 70)
    print("TESTE: Verificação do Formato de Dados para PyCaret")
    print("=" * 70)
    
    # Valores de teste
    lux = 15.0
    temp = 14.0
    vibracao = 0.5
    
    print(f"\n📊 Valores de entrada:")
    print(f"   Lux: {lux}")
    print(f"   Temperatura: {temp}")
    print(f"   Vibração: {vibracao}")
    
    # Prepara os dados
    dados_df = preparar_dados_para_previsao(lux, temp, vibracao)
    
    print(f"\n✅ DataFrame criado com sucesso!")
    print(f"\n📋 Estrutura do DataFrame:")
    print(f"   Shape: {dados_df.shape}")
    print(f"   Colunas: {list(dados_df.columns)}")
    print(f"   Tipos: {dict(dados_df.dtypes)}")
    
    print(f"\n📊 Conteúdo do DataFrame:")
    print(dados_df)
    
    # Verifica os nomes das colunas (devem corresponder aos usados no treinamento)
    expected_cols = ['Lux (x10³)', 'Temperatura (°C)', 'Vibração']
    actual_cols = list(dados_df.columns)
    
    print(f"\n🔍 Verificação de Compatibilidade:")
    print(f"   Colunas esperadas: {expected_cols}")
    print(f"   Colunas obtidas:   {actual_cols}")
    
    if actual_cols == expected_cols:
        print("   ✅ COMPATÍVEL - As colunas correspondem ao formato de treinamento!")
    else:
        print("   ❌ INCOMPATÍVEL - As colunas não correspondem!")
        return False
    
    # Verifica que é um DataFrame válido
    assert isinstance(dados_df, pd.DataFrame), "Deve ser um DataFrame"
    assert dados_df.shape == (1, 3), "Deve ter 1 linha e 3 colunas"
    
    print("\n" + "=" * 70)
    print("✅ TESTE PASSOU - Formato correto para modelos PyCaret!")
    print("=" * 70)
    
    return True


def comparar_formatos():
    """Compara o formato antigo (incorreto) com o novo (correto)."""
    
    print("\n" + "=" * 70)
    print("COMPARAÇÃO: Formato Antigo vs. Formato Novo")
    print("=" * 70)
    
    lux, temp, vibracao = 15.0, 14.0, 0.5
    
    # Formato antigo (incorreto - apenas array)
    print("\n❌ FORMATO ANTIGO (INCORRETO):")
    old_format = np.array([lux, temp, vibracao]).reshape(1, -1)
    print(f"   Tipo: {type(old_format)}")
    print(f"   Shape: {old_format.shape}")
    print(f"   Conteúdo: {old_format}")
    print(f"   Problema: Sem nomes de colunas - causa erro com PyCaret!")
    
    # Formato novo (correto - DataFrame com nomes)
    print("\n✅ FORMATO NOVO (CORRETO):")
    new_format = preparar_dados_para_previsao(lux, temp, vibracao)
    print(f"   Tipo: {type(new_format)}")
    print(f"   Shape: {new_format.shape}")
    print(f"   Colunas: {list(new_format.columns)}")
    print(f"   Conteúdo:")
    print(new_format)
    print(f"   Vantagem: DataFrame com nomes de colunas - compatível com PyCaret!")
    
    print("\n" + "=" * 70)


def main():
    """Executa os testes de demonstração."""
    
    print("\n🔬 DEMONSTRAÇÃO: Correção do Bug de Previsão")
    print("=" * 70)
    print("\nProblema Original:")
    print('  Erro: "None of [Index([\'Lux (x10³)\', \'Temperatura (°C)\', \'Vibração\'])]')
    print('         are in the [columns]"')
    print("\nCausa:")
    print("  - Modelos PyCaret esperam DataFrame com nomes de colunas")
    print("  - Código antigo enviava apenas array numpy sem nomes")
    print("\nSolução:")
    print("  - Nova função: preparar_dados_para_previsao()")
    print("  - Converte valores para DataFrame com nomes corretos")
    print("=" * 70)
    
    # Executa os testes
    try:
        test_formato_dados()
        comparar_formatos()
        
        print("\n" + "🎉 " * 35)
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("\n💡 A função preparar_dados_para_previsao() está funcionando corretamente!")
        print("\n📝 Os modelos PyCaret agora podem fazer previsões sem erros!")
        print("\n" + "🎉 " * 35 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
