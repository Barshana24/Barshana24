<!--
  The sheets in assets/ are generated. Edit tools/build_panels.py and re-run it:
      python tools/build_panels.py
  Changes show up within about five minutes (raw.githubusercontent sends
  max-age=300). Do NOT add a ?v= cache-busting param to these URLs. A unique
  query string is a fresh CDN cache key, so every visitor misses the edge cache
  and hits origin, and origin is what gets rate limited into HTTP 429.

  Three things that look odd here but are deliberate:
  - Each sheet ships twice. A 1000-wide sheet scaled into a phone's ~390px
    README column renders body text at about 5px. The <picture> media query
    hands phones a 480-wide single-column variant instead, where the same type
    comes out more than twice the size. Both branches carry the same content.
  - Images point at raw.githubusercontent.com, not relative paths. GitHub
    rewrites relative paths to github.com/<owner>/<repo>/raw/..., which 404s.
  - All eight panels live in two files per width, split only where real HTML
    links are needed in between. Fewer requests keeps more of them served from
    the CDN edge rather than origin.
-->

<picture>
  <source media="(max-width: 600px)" srcset="https://raw.githubusercontent.com/Barshana24/Barshana24/main/assets/sheet-1-sm.svg">
  <img src="https://raw.githubusercontent.com/Barshana24/Barshana24/main/assets/sheet-1.svg" width="100%" alt="Barshana Chatterjee, at Barshana24, Kolkata India. I build things that put AI to work on real data, usually on a local model. Most of what I ship runs fully offline: no API keys, and nothing leaves the machine it runs on. Operating principle: if a model can run on the machine that already holds the data, it should. Current focus: local-LLM tooling, agent benchmarks, RF and DSP. Signals: 14 public repositories, 6 shipped tools, 3 upstream pull requests, 1 publication. Stack weighted by use: Python, TypeScript, SQL, JavaScript, MATLAB, Ollama and local LLMs, FastAPI, React and Next.js, PostgreSQL, BigQuery. Pipeline: ingest, store, reason on a local model, serve, interface.">
</picture>

<p align="center">
  <a href="https://barshana24.github.io/portfolio_personal/"><img src="https://img.shields.io/badge/PORTFOLIO-0d1117?style=for-the-badge&logo=googlechrome&logoColor=22d3ee&labelColor=0d1117" alt="Portfolio"></a>
  <a href="https://www.linkedin.com/in/barshana-chatterjee"><img src="https://img.shields.io/badge/LINKEDIN-0d1117?style=for-the-badge&logo=linkedin&logoColor=22d3ee&labelColor=0d1117" alt="LinkedIn"></a>
  <a href="mailto:barshanachatterjee@gmail.com"><img src="https://img.shields.io/badge/EMAIL-0d1117?style=for-the-badge&logo=gmail&logoColor=22d3ee&labelColor=0d1117" alt="Email"></a>
</p>

<picture>
  <source media="(max-width: 600px)" srcset="https://raw.githubusercontent.com/Barshana24/Barshana24/main/assets/sheet-2-sm.svg">
  <img src="https://raw.githubusercontent.com/Barshana24/Barshana24/main/assets/sheet-2.svg" width="100%" alt="Work manifest, six selected projects. technical-doc-generator in Python: point it at a codebase and get back a README, an API reference, a UML diagram, and inline comments, fully offline on a local model. ai-code-reviewer in TypeScript: scores code across ten quality dimensions and exports a PDF report, no cloud API keys required. Token_minimiser in JavaScript: Chrome extension that shrinks prompts before they reach ChatGPT, Claude, or Gemini, 15 to 45 percent fewer tokens. FunellQ in TypeScript: funnel analytics on Google's public GA4 e-commerce dataset that sizes the biggest leak in real revenue. Siglo-GTM-tool in Python: scores signals, member targets, and open opportunities into a ranked list of business development plays. EduBot in TypeScript: study assistant for engineering students in their own language. Upstream: AOBench is a role-aware, permission-enforced benchmark for AI agents that operate HPC systems, and I work on its command line interface, with pull requests 43, 47, and 50. Drawn by Barshana Chatterjee, Kolkata India, open to collaboration.">
</picture>

<p align="center">
  <a href="https://github.com/Barshana24/technical-doc-generator">technical-doc-generator</a> &middot;
  <a href="https://github.com/Barshana24/ai-code-reviewer">ai-code-reviewer</a> &middot;
  <a href="https://github.com/Barshana24/Token_minimiser">Token_minimiser</a> &middot;
  <a href="https://github.com/Barshana24/FunellQ">FunellQ</a> &middot;
  <a href="https://github.com/Barshana24/Siglo-GTM-tool">Siglo-GTM-tool</a> &middot;
  <a href="https://github.com/Barshana24/EduBot">EduBot</a>
</p>

<p align="center">
  <a href="https://github.com/MSKazemi/aobench/pull/43"><img src="https://img.shields.io/github/pulls/detail/state/MSKazemi/aobench/43?style=for-the-badge&label=PR%20%2343&labelColor=0d1117" alt="AOBench pull request 43"></a>
  <a href="https://github.com/MSKazemi/aobench/pull/47"><img src="https://img.shields.io/github/pulls/detail/state/MSKazemi/aobench/47?style=for-the-badge&label=PR%20%2347&labelColor=0d1117" alt="AOBench pull request 47"></a>
  <a href="https://github.com/MSKazemi/aobench/pull/50"><img src="https://img.shields.io/github/pulls/detail/state/MSKazemi/aobench/50?style=for-the-badge&label=PR%20%2350&labelColor=0d1117" alt="AOBench pull request 50"></a>
</p>

<p align="center">
  <a href="https://barshana24.github.io/portfolio_personal/"><img src="https://img.shields.io/badge/PORTFOLIO-0d1117?style=for-the-badge&logo=googlechrome&logoColor=22d3ee&labelColor=0d1117" alt="Portfolio"></a>
  <a href="https://www.linkedin.com/in/barshana-chatterjee"><img src="https://img.shields.io/badge/LINKEDIN-0d1117?style=for-the-badge&logo=linkedin&logoColor=22d3ee&labelColor=0d1117" alt="LinkedIn"></a>
  <a href="mailto:barshanachatterjee@gmail.com"><img src="https://img.shields.io/badge/EMAIL-0d1117?style=for-the-badge&logo=gmail&logoColor=22d3ee&labelColor=0d1117" alt="Email"></a>
</p>
