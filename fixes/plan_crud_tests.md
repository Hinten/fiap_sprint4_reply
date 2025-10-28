Plano de Ação — Correção dos testes CRUD

Resumo

Executei a suíte de testes CRUD (comando: `tests\run_tests.bat crud`), porém o runner não retornou saída de execução no ambiente atual; mesmo assim inspecionei os testes e os models para identificar inconsistências aparentes que causariam falhas ao rodar os testes localmente.

Principais problemas identificados

1) Inconsistência de nomes de atributos de relacionamento entre models e testes
   - `src/database/models/sensor.py` define no `TipoSensor` o atributo de relacionamento como `sensors` (em inglês).
   - `src/database/models/equipamento.py` define o atributo de relacionamento como `sensores` (em português).
   - Em `tests/crud/test_sensor_crud.py` há usos mistos de `TipoSensor.sensores` (joinload) e `tipo_sensor_fixture.sensors` (assert). Isto causará AttributeError/InvalidRequest quando os testes tentarem acessar o atributo inexistente.

2) (Potencial) Falta de output ao executar pytest no ambiente
   - Comandos para rodar pytest não geraram saída no terminal de execução automatizada. Isso pode ser um problema do ambiente (pytest não instalado) ou do canal de execução aqui. Recomenda-se rodar localmente se persistir.

Ações propostas (passos)

1) Corrigir testes inconsistentes
   - Atualizar `tests/crud/test_sensor_crud.py` para usar `TipoSensor.sensors` (consistência com o model `TipoSensor`) no `joinedload` e demais acessos.
   - Revisar todo o diretório `tests/crud/` buscando outros usos incoerentes entre `sensores` e `sensors` e unificar conforme os models (preferir o nome definido no model).

2) Validar model naming
   - Alternativa: se a intenção do projeto for usar nomes em português (`sensores`) para todos os relacionamentos, alterar o `TipoSensor` para declarar `sensores` em vez de `sensors`. Essa mudança tem impacto maior e exige alteração em mais locais; portanto preferi ajustar os testes (menor blast radius).

3) Executar a suíte de testes CRUD localmente
   - Depois das correções, rodar: `tests\run_tests.bat crud` e coletar saída completa para verificar outras falhas (integrity errors, falta de constraints, imports faltando, etc.).

4) Corrigir erros de models/fixtures se aparecerem
   - Se ocorrerem IntegrityError por chaves únicas, ajustar dados dos fixtures (usar cnpj/nomes diferentes) ou modificar models para aceitar duplicatas conforme o design.

5) Atualizar a pasta `fixes/` com um checklist e resultados das execuções.

Arquivo(s) a editar agora (mudanças propostas imediatas)

- tests/crud/test_sensor_crud.py: Substituir `joinedload(TipoSensor.sensores)` por `joinedload(TipoSensor.sensors)` (linha onde o joinedload usa o atributo errado). Revisar asserções correspondentes. Esta é uma correção de baixo risco e alinhada ao model atual.

Status atual (executado por mim):

- Inspeção dos testes e models realizada.
- Corrigi um problema de inconsistência no arquivo `tests/crud/test_sensor_crud.py` (uso de `TipoSensor.sensores` vs `TipoSensor.sensors`). Agora o teste usa `TipoSensor.sensors` para ficar consistente com `src/database/models/sensor.py`.
- Criei este plano de ação (arquivo atual) em `fixes/plan_crud_tests.md`.
- Rodadas de pytest no ambiente automatizado retornaram saída vazia (sem logs) — não foi possível coletar o resultado completo dos testes aqui.
- Verificação estática rápida (ferramenta de erros) não encontrou erros de sintaxe nos arquivos alterados.

Próximos passos (o que eu preciso que você rode localmente e me traga o resultado):

1) Assegure que as dependências estejam instaladas (recomendo criar um venv e instalar as dependências do projeto):

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

2) Rode a suíte de testes CRUD e salve o output em um arquivo (isso evita perda de logs):

```bat
tests\run_tests.bat crud > tests_crud_output.txt 2>&1
```

ou diretamente com pytest para output mais verboso:

```bat
python -m pytest tests/crud/ -vv > tests_crud_output.txt 2>&1
```

3) Anexe o arquivo `tests_crud_output.txt` ou cole o conteúdo aqui para eu analisar as falhas restantes.

Se você preferir, posso continuar com uma auditoria adicional estática (procurar por outros potenciais problemas) e aplicar correções de baixo risco automaticamente. A seguir listo mudanças adicionais de baixo risco que posso aplicar sem execuções de teste:

- Unificar terminologia de relacionamentos nos models (por exemplo escolher entre `sensors` vs `sensores`) e adaptar os testes para o mesmo padrão. Atualmente preferi adaptar os testes ao model existente (`TipoSensor.sensors`). Se preferir a versão em PT-BR para tudo, posso alterar o model e atualizar todos os testes.
- Verificar fixtures que usam o mesmo valor de campo único (por exemplo `nome`, `cnpj`) e transformar os dados em únicos por fixture para evitar IntegrityError indesejados.

Checklist (resumo)

- [x] Inspecionar testes `tests/crud/` e models relacionados
- [x] Criar plano inicial em `fixes/plan_crud_tests.md`
- [x] Corrigir `tests/crud/test_sensor_crud.py` para usar `TipoSensor.sensors`
- [ ] Executar testes CRUD e coletar falhas (bloqueado — ambiente atual não retornou saída)
- [ ] Corrigir erros detectados no log dos testes e reexecutar até ficar verde

Observação final

Devido à ausência de logs na execução de pytest aqui, preciso que você rode os comandos acima no seu ambiente local (Windows) e envie o output (arquivo ou colado). Assim poderei continuar aplicando correções diretamente no repositório até que os testes passem.
