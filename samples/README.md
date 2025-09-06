# Code and System Design Samples

**Note:** These samples (especially the older ones) may not accurately reflect my current views and knowledge on specific topics. I've kept them faithful to their original versions to offer a clearer insight into how I've approached problems and designed solutions over time.

---

### [Homepage/Portfolio](https://github.com/isaacbernat/homepage)
- The source code for my personal portfolio, [isaacbernat.com](https://www.isaacbernat.com). The project itself is a meta-demonstration of my engineering philosophy.
- Built with a custom Static Site Generator (SSG) in Node.js, following a modern **Jamstack architecture**.
- Written in **mid 2025**, prioritizing performance, accessibility and a robust CI/CD pipeline with programmatic quality gates (ESLint, Prettier).
- The repository's [README](https://github.com/isaacbernat/homepage/blob/main/README.md) offers a deep dive into the architectural decisions, guiding principles and technical roadmap.

### [Spam Classification System Design](https://www.isaacbernat.com/assets/spam_classifier.pdf)
- A comprehensive, production-grade technical design for a heuristic-based spam classification engine.
- The design proposes a pragmatic, "white-box" heuristic approach for a legacy Perl ecosystem which prioritizes interpretability and maintainability.
- Written in **mid 2025** as part of a self-directed professional development period.
- The document details the core architecture, a multi-layered testing strategy and a low-risk phased path to a production ML service.

### [reimbursement-system](https://github.com/isaacbernat/cv/tree/master/samples/reimbursement-system)
- A minimal system for handling healthcare reimbursements via a RESTful API.
- Features a microservice architecture using containerized Python and PostgreSQL services.
- Written in **late 2017** as a code assignment.
- The included README describes the project setup, design decisions and potential future improvements.

### [gae-shorten](https://github.com/isaacbernat/gae-shorten)
- A high-performance URL shortener implemented in under 100 lines of Python for Google App Engine.
- Written in **mid 2012** as a code assignment.
- The included README details the design rationale, deployment instructions and long-term scalability considerations.

### [docker-pudb](https://github.com/isaacbernat/docker-pudb)
- A minimal working example for debugging Python code remotely within a Docker container using `pudb`.
- Written in **mid 2018** during a company "hack day".

### [tinymem](https://github.com/isaacbernat/tinymem)
- A complete memory game for the Thumby keychain console, written in under 50 lines of MicroPython.
- Written in **late 2021** over a weekend.

---
**PS:** Some projects are included as Git submodules. After cloning, run `git submodule init` and `git submodule update` to fetch their source code.
