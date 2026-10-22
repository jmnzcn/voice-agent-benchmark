# 🎙️ Voice Agent Benchmark

**¿Qué combinación de STT + LLM + TTS conviene para un agente de voz en español?**
Medí 15 servicios (12 en la nube y 3 locales) en latencia, precisión, costo, privacidad, customización e integración, y armé 4 stacks completos de voz a voz para ver qué pasa en un turno real de conversación.

[![tests](https://github.com/jmnzcn/voice-agent-benchmark/actions/workflows/test.yml/badge.svg)](https://github.com/jmnzcn/voice-agent-benchmark/actions/workflows/test.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Servicios](https://img.shields.io/badge/servicios-15-0A66C2)
![Llamadas](https://img.shields.io/badge/llamadas_medidas-700-2EA44F)
![Local](https://img.shields.io/badge/local-Ollama%20%C2%B7%20faster--whisper%20%C2%B7%20Piper-555)

[English summary](#-english-summary) · [Resultados](#-resultados-clave) · [Metodología](#-metodología) · [Cómo reproducirlo](#-cómo-reproducirlo)

---

## 📊 Resultados clave

![Desglose de latencia por etapa en los 4 stacks E2E](docs/graficos_generados/e2e_desglose_latencia.png)

| Stack (STT → LLM → TTS) | Latencia por turno (prom.) | Costo por turno | Para qué sirve |
|---|---:|---:|---|
| ⚡ **Deepgram → Groq → Google** | **1,8 s** | **$0,0072** | Demos y producción de baja latencia |
| ☁️ Azure → GPT-4o → Azure | 7,8 s | $0,0087 | Empresas que ya están en Azure |
| 💎 AssemblyAI → GPT-4o → ElevenLabs | 9,0 s | $0,0877 | Máxima calidad de voz |
| 🔒 faster-whisper → Ollama → Piper | 62,0 s | $0 | Datos que no pueden salir de la máquina |

*25 turnos por stack (5 audios × 5 corridas).*

**Lo que encontré:**

1. **El stack más rápido también fue el más barato.** Deepgram + Groq + Google respondió en 1,8 s por turno: **~5× más rápido y ~12× más barato** que el stack premium. Más caro no significa mejor experiencia conversacional.
2. **El STT local casi empata con el mejor de la nube.** faster-whisper large-v3 logró un WER de **5,0 %**, contra 4,7 % de AssemblyAI (el mejor), a costo de API $0. El precio es la latencia: ~37 s por audio en una GPU de 4 GB.
3. **Groq domina la latencia de LLM:** 695 ms en promedio y **227 ms al primer token**, ~2,5× más rápido que GPT-4o y ~9–10× más que Claude Sonnet 4.6 o Gemini 2.5 Flash.
4. **No todos los LLM respetan un esquema JSON.** OpenAI, Anthropic y Groq devolvieron JSON válido el 100 % de las veces; Ollama (Llama 3.2 3B) el 80 % y Gemini 2.5 Flash solo el 60 %.
5. **En TTS, la diferencia de precio es enorme.** ElevenLabs tuvo la mejor naturalidad (5/5) pero cuesta **~19×** lo que Google Neural2, que además fue el más rápido (300 ms).
6. **Lo 100 % local es viable para privacidad, no para tiempo real** en hardware modesto: 62 s por turno, con el STT como cuello de botella (~78 % del tiempo).

<table>
<tr>
<td width="50%"><img src="docs/graficos_generados/llm_latencia_vs_costo.png" alt="LLM: latencia vs costo"></td>
<td width="50%"><img src="docs/graficos_generados/stt_quality.png" alt="STT: WER promedio"></td>
</tr>
<tr>
<td align="center"><sub>LLM: latencia vs. costo por llamada</sub></td>
<td align="center"><sub>STT: WER promedio (menor es mejor)</sub></td>
</tr>
</table>

### Matriz completa

| Categoría | Servicio | Modelo | Latencia prom. | Calidad | USD/llamada | Privacidad (1–5) |
|---|---|---|---:|---|---:|:---:|
| LLM | Groq | llama-3.3-70b-versatile | **695 ms** | JSON 100 % · coherencia 4/5 | 0,0002 | 4 |
| LLM | OpenAI | gpt-4o | 1.781 ms | JSON 100 % · coherencia 5/5 | 0,0020 | 3 |
| LLM | Google | gemini-2.5-flash | 5.928 ms | JSON 60 % · coherencia 4/5 | 0,0008 | 3 |
| LLM | Anthropic | claude-sonnet-4-6 | 6.916 ms | JSON 100 % · coherencia 5/5 | 0,0057 | 4 |
| LLM | Ollama (local) | llama3.2:3b | 36.643 ms | JSON 80 % · coherencia 3/5 | 0 | **5** |
| STT | Deepgram | nova-3 | **429 ms** | WER 6,6 % | 0,0013 | 3 |
| STT | OpenAI | whisper-1 | 2.127 ms | WER 6,5 % | 0,0018 | 3 |
| STT | AssemblyAI | universal-3-pro | 4.218 ms | **WER 4,7 %** | 0,0011 | 3 |
| STT | Azure | speech-recognition-standard | 6.892 ms | WER 7,1 % | 0,0049 | 3 |
| STT | faster-whisper (local) | large-v3 | 37.482 ms | WER 5,0 % | 0 | **5** |
| TTS | Google | es-ES-Neural2-A | **300 ms** | naturalidad 4/5 | 0,0027 | 3 |
| TTS | Azure | es-CR-MariaNeural | 849 ms | naturalidad 4/5 | 0,0027 | 3 |
| TTS | ElevenLabs | eleven_multilingual_v2 | 2.148 ms | **naturalidad 5/5** | 0,0512 | 3 |
| TTS | Piper (local) | es_ES-davefx-medium | 3.026 ms | naturalidad 3/5 | 0 | **5** |
| TTS | OpenAI | gpt-4o-mini-tts | 3.369 ms | naturalidad 4/5 | 0,1024 | 3 |

Más detalle (TTFT, WER por fuente de audio, MOS, customización, integración): [`docs/dimensiones_datos/`](docs/dimensiones_datos/). Todos los gráficos: [`docs/graficos_generados/`](docs/graficos_generados/).

---

## 🧭 ¿Cuál elegir?

- **Necesito que se sienta como una conversación** → Deepgram + Groq + Google TTS.
- **Necesito la voz más natural** (marca, narración) → ElevenLabs, y GPT-4o o Claude para el razonamiento.
- **Necesito salidas estructuradas confiables** (tool calling, JSON) → GPT-4o, Claude o Groq.
- **Los datos no pueden salir de la organización** → faster-whisper + Ollama + Piper, con una GPU más potente que la de esta prueba.
- **Ya estoy en Azure** → el stack Azure da un costo similar al rápido, con más latencia.

---

## 🔬 Metodología

- **Protocolo:** 5 corridas por input. LLM con 5 prompts (incluye uno que exige JSON estricto), TTS con 5 textos y STT con 14 audios en español (con SHA-256 para verificar que son los mismos).
- **E2E:** 4 stacks completos STT → LLM → TTS, con 5 audios por stack.
- **Latencia:** tiempo total por llamada; en LLM también el tiempo al primer token (TTFT) con streaming.
- **Precisión:** WER con `jiwer` en STT; revisión manual de coherencia y validación de JSON en LLM; MOS de inteligibilidad (round-trip con STT) y naturalidad por escucha en TTS.
- **Costo:** USD por llamada con las tarifas públicas en [`common/rates.py`](common/rates.py).
- **Privacidad, customización e integración:** escala 1–5 con criterios en [`analysis/dimensions_catalog.py`](analysis/dimensions_catalog.py).
- **Hardware local:** Windows 11, 12 CPU lógicos, 32 GB RAM, NVIDIA Quadro P2000 (4 GB VRAM). Los resultados locales mejorarían mucho con una GPU actual.

**Limitaciones:** es una sola corrida desde Costa Rica, así que la latencia de la nube incluye la red; los puntajes de MOS y coherencia son de un solo evaluador; y las tarifas cambian con el tiempo. Los CSV crudos están en [`results/`](results/) para que cualquiera revise o rehaga el análisis.

![Arquitectura del pipeline](docs/graficos_generados/pipeline_comunicacion.png)

---

## 🚀 Cómo reproducirlo

Requisitos: Python 3.11+, Git y FFmpeg. Para los servicios locales: Ollama (`llama3.2:3b`), GPU recomendable para faster-whisper y Piper configurado con las variables `PIPER_*` de `.env.example`. Si falta la API key de un proveedor, ese servicio se omite y el resto sigue.

```powershell
git clone https://github.com/jmnzcn/voice-agent-benchmark.git
cd voice-agent-benchmark

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # completar las keys que tengas

python scripts/bootstrap.py
```

**Solo regenerar tablas y gráficos** a partir de los CSV incluidos (no gasta créditos):

```powershell
python scripts/run_analysis.py
```

**Corrida completa** (usa las APIs y tarda bastante en local):

```powershell
python -m run_all 5
python scripts/validate_results.py
python scripts/run_analysis.py
```

<details>
<summary>Otros comandos</summary>

```powershell
python -m run_all 5 --skip-e2e
python -m benchmarks.pipeline.run_e2e 5
python scripts/dedupe_results.py      # si re-corriste inputs sin reset_results
python scripts/reset_results.py
python scripts/run_analysis.py --with-optional   # recalcula MOS de inteligibilidad con Whisper en CPU (lento)
python scripts/smoke_analysis.py
python -m pytest tests/ -q
```

Para regenerar los audios de prueba desde cero: [`data/test_audio/README.md`](data/test_audio/README.md).
</details>

<details>
<summary>Estructura del repositorio</summary>

```text
run_all.py                 entrada única de la corrida
benchmarks/                llm/, stt/, tts/, pipeline/ (E2E)
common/                    prompts, textos TTS, catálogo STT, tarifas
analysis/                  agregación, estadísticas, gráficos
data/                      14 audios WAV, transcripciones de referencia, notas de calidad
results/                   CSV de la corrida, manifiesto, hardware y red
docs/dimensiones_datos/    tablas por dimensión (Markdown)
docs/graficos_generados/   gráficos PNG
docs/pipeline.puml         diagrama UML del pipeline
examples/                  cliente C# de ejemplo para Unity
scripts/                   bootstrap, análisis, validación
tests/                     pytest
```
</details>

<details>
<summary>Seguridad: qué nunca se sube</summary>

- `.env` y cualquier archivo con keys (`secrets/`, JSON de cuenta de GCP). Solo se versiona `.env.example`, vacío.
- `models/`, el binario de Piper (`tools/piper/`), `results/raw/` y `results/tts_outputs/`.

`python scripts/bootstrap.py` avisa si `.env` quedó trackeado por error.
</details>

---

## 🇺🇸 English summary

I benchmarked **15 speech and language services** (12 cloud, 3 fully local) for a **Spanish-speaking voice agent**, across latency, accuracy, cost, privacy, customization and integration effort, plus **4 end-to-end STT → LLM → TTS stacks**.

- **Fastest stack was also the cheapest:** Deepgram → Groq → Google TTS answered in **1.8 s per turn at $0.007**, about 5× faster and 12× cheaper than the premium stack (AssemblyAI → GPT-4o → ElevenLabs).
- **Local STT nearly matches the best cloud option:** faster-whisper large-v3 reached **5.0 % WER** vs. 4.7 % for AssemblyAI, at $0 API cost, but ~37 s per clip on a 4 GB GPU.
- **Groq leads LLM latency** (695 ms average, 227 ms to first token). OpenAI, Anthropic and Groq returned valid JSON 100 % of the time; Gemini 2.5 Flash only 60 %.
- **TTS pricing varies ~19×** between ElevenLabs (best naturalness) and Google Neural2 (fastest).
- **Fully offline is viable for privacy, not real time** on modest hardware (62 s per turn).

Everything is reproducible: raw CSVs, SHA-256-verified test audio and scripts that rebuild every table and chart without spending API credits.

---

## 🎓 Contexto académico

Proyecto 2 del curso PF-3312 Laboratorio de Agentes Virtuales Inteligentes (Dr. Alexander Barquero), Posgrado en Computación e Informática, Universidad de Costa Rica, I ciclo 2026. Informe completo: [`docs/informe_PF3312_Proyecto2_B03230.pdf`](docs/informe_PF3312_Proyecto2_B03230.pdf).

Los servicios pertenecen a sus proveedores; FLEURS, Common Voice y los demás datasets citados tienen su propia licencia.

**Uso de herramientas de IA:** usé ChatGPT (OpenAI) y Claude (Anthropic) como apoyo para organizar ideas y revisar la redacción. El diseño del experimento, las mediciones, el análisis y las conclusiones son de mi autoría.

---

**Ney Fred Jiménez Campos** · [LinkedIn](https://www.linkedin.com/in/neyfred/) · [GitHub](https://github.com/jmnzcn) · neyfred@gmail.com
