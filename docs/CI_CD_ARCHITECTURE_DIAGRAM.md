# CI/CD Architecture Diagrams

These diagrams can be rendered on GitHub, in VS Code with Mermaid extensions, or on https://mermaid.live/

---

## Complete CI/CD Flow

```mermaid
graph TB
    subgraph "Developer Workflow"
        A[Create Feature Branch] --> B[Write Code & Tests]
        B --> C[Push & Open PR]
    end

    subgraph "PR Validation - pr-checks.yml"
        C --> D{PR to Protected Branch?}
        D -->|Yes| E[Security Scan - Fail Fast]
        D -->|No| F[Security Scan - Warn Only]
        E --> G[Linting - ruff]
        F --> G
        G --> H[Type Checking - mypy]
        H --> I[Unit Tests + Coverage]
        I --> J{To develop/main/release?}
        J -->|Yes| K[Validate CHANGELOG]
        J -->|No| L[Skip CHANGELOG]
        K --> M[PR Summary]
        L --> M
    end

    M --> N{Approved?}
    N -->|No| B
    N -->|Yes| O[Merge PR]

    subgraph "Post-Merge - version-and-build.yml"
        O --> P{Is PR Merge?}
        P -->|Yes| Q[Bump Version]
        P -->|No| R[Use Current Version]
        Q --> S{Branch Type?}
        R --> S

        S -->|develop| T1[Increment Alpha<br/>1.11.0a4 → 1.11.0a5]
        S -->|release/X.Y.Z| T2{First Commit?}
        S -->|main| T3[Strip Pre-release<br/>1.11.0rc3 → 1.11.0]
        S -->|hotfix/X.Y.Z| T4[Bump Patch<br/>1.11.0 → 1.11.1]

        T2 -->|Yes| T2A[Alpha → RC1<br/>1.11.0a5 → 1.11.0rc1]
        T2 -->|No| T2B[Increment RC<br/>1.11.0rc2 → 1.11.0rc3]

        T1 --> U{Run Integration Tests?}
        T2A --> U
        T2B --> U
        T3 --> U
        T4 --> U

        U -->|develop or release| V[Integration Tests<br/>with EDL Creds]
        U -->|main or hotfix| W[Skip Integration Tests]

        V --> X[Build Python Package]
        W --> X

        X --> Y{Branch?}
        Y -->|develop/main/release| Z1[Create Git Tag]
        Y -->|hotfix| Z1
        Y -->|other| Z2[No Tag]

        Z1 --> AA{Publish?}
        Z2 --> AB[Build Complete]

        AA -->|release| AC[Publish to Test PyPI]
        AA -->|other| AD[No Publish]

        AC --> AE{Build Docker?}
        AD --> AE

        AE -->|develop or release| AF[Build & Push Docker<br/>Tags: venue + version]
        AE -->|other| AG[No Docker Build]

        AF --> AH[Update Snyk Monitor]
        AG --> AH
    end

    subgraph "Release Branch Created"
        T2A -.Triggers.-> RP[auto-bump-develop.yml]
        RP --> RQ{develop on release version?}
        RQ -->|Yes| RR[Bump develop to next minor<br/>1.11.0a5 → 1.12.0a1]
        RQ -->|No| RS[Skip - already bumped]
        RR --> RT[Push with [skip ci]]
    end

    subgraph "Production Release - publish.yml"
        AI[Maintainer Creates<br/>GitHub Release] --> AJ[Extract Version from Tag]
        AJ --> AK[Verify Tag Matches pyproject.toml]
        AK --> AL[Build Python Package]
        AL --> AM[Publish to PyPI<br/>Production]
        AM --> AN[Build & Push Docker<br/>Tags: ops, latest, version]
        AN --> AO[Update Snyk Monitor<br/>Production]
    end

    subgraph "External Contributors"
        EXT1[Fork Repository] --> EXT2[Make Changes]
        EXT2 --> EXT3[Open PR from Fork]
        EXT3 --> EXT4[pull-request-received.yml]
        EXT4 --> EXT5[Run Unit Tests Only<br/>No Secrets Access]
        EXT5 --> EXT6{Tests Pass?}
        EXT6 -->|Yes| EXT7[Maintainer Reviews]
        EXT6 -->|No| EXT2
        EXT7 --> O
    end

    style A fill:#e1f5e1
    style O fill:#fff3cd
    style AI fill:#f8d7da
    style M fill:#cfe2ff
    style Q fill:#d1ecf1
    style AM fill:#d4edda
    style V fill:#ffeaa7
    style AF fill:#74b9ff
```

---

## Branching Strategy

```mermaid
gitGraph
    commit id: "Initial"
    branch develop
    checkout develop
    commit id: "Feature 1" tag: "1.11.0a1"
    commit id: "Feature 2" tag: "1.11.0a2"
    commit id: "Feature 3" tag: "1.11.0a3"
    commit id: "Feature 4" tag: "1.11.0a4"
    commit id: "Feature 5" tag: "1.11.0a5"

    branch release/1.11.0
    checkout release/1.11.0
    commit id: "Start RC" tag: "1.11.0rc1"

    checkout develop
    commit id: "Start next minor" tag: "1.12.0a1"
    commit id: "Continue dev" tag: "1.12.0a2"

    checkout release/1.11.0
    commit id: "Fix bug 1" tag: "1.11.0rc2"
    commit id: "Fix bug 2" tag: "1.11.0rc3"

    checkout main
    merge release/1.11.0 tag: "1.11.0"

    checkout develop
    merge main

    checkout main
    branch hotfix/1.11.1
    commit id: "Urgent fix" tag: "1.11.1"

    checkout main
    merge hotfix/1.11.1

    checkout develop
    merge hotfix/1.11.1
```

---

## Version Bumping Decision Tree

```mermaid
flowchart TD
    A[PR Merged to Protected Branch] --> B{Check Commit Message}
    B -->|"Merge pull request"| C{Which Branch?}
    B -->|Direct Push| D[Skip Version Bump<br/>Use Current Version]

    C -->|develop| E[Increment Alpha<br/>bump pre_number]
    C -->|release/X.Y.Z| F{Current Version?}
    C -->|main| G{Has Pre-release Label?}
    C -->|hotfix/X.Y.Z| H{Has Pre-release Label?}

    E --> E1[Example: 1.11.0a4 → 1.11.0a5]
    E1 --> V1[Venue: sit]
    V1 --> END1[Create Tag]

    F -->|Contains 'a'| I[Alpha → RC1<br/>bump pre_label]
    F -->|Contains 'rc'| J[Increment RC<br/>bump pre_number]

    I --> I1[Example: 1.11.0a5 → 1.11.0rc1]
    I1 --> I2[Trigger auto-bump-develop.yml]
    I2 --> I3[Develop: 1.11.0a5 → 1.12.0a1]
    I1 --> V2[Venue: uat]
    V2 --> P1[Publish to Test PyPI]
    P1 --> END2[Create Tag]

    J --> J1[Example: 1.11.0rc2 → 1.11.0rc3]
    J1 --> V3[Venue: uat]
    V3 --> P2[Publish to Test PyPI]
    P2 --> END3[Create Tag]

    G -->|Yes rc or a| K[Strip Pre-release<br/>bump pre_label]
    G -->|No| L[Already Final<br/>No Change]

    K --> K1[Example: 1.11.0rc3 → 1.11.0]
    L --> L1[Example: 1.11.0 stays 1.11.0]
    K1 --> V4[Venue: ops]
    L1 --> V4
    V4 --> END4[Create Tag<br/>Ready for Release]

    H -->|Yes| M[Strip Pre-release]
    H -->|No| N[Already Final]
    M --> O[Bump Patch]
    N --> O

    O --> O1[Example: 1.11.0 → 1.11.1]
    O1 --> V5[Venue: ops]
    V5 --> END5[Create Tag]

    D --> V6[Venue Based on Branch]
    V6 --> END6[Build Only<br/>No Tag Created]

    style E fill:#d1ecf1
    style I fill:#ffeaa7
    style J fill:#ffeaa7
    style K fill:#d4edda
    style O fill:#f8d7da
```

---

## Workflow Dependencies

```mermaid
flowchart LR
    subgraph "Reusable Workflows"
        UT[unit-tests.yml]
        IT[integration-tests.yml]
        DB[docker-build.yml]
    end

    subgraph "Main Workflows"
        PR[pr-checks.yml]
        VB[version-and-build.yml]
        PUB[publish.yml]
        PRR[pull-request-received.yml]
        ABD[auto-bump-develop.yml]
    end

    PR -.calls.-> UT
    VB -.calls.-> IT
    VB -.calls.-> DB
    PUB -.calls.-> DB
    PRR -.calls.-> UT

    PR -->|PR Merged| VB
    VB -->|Release Branch Created| ABD
    VB -->|Tag Created on main| PUB

    style UT fill:#cfe2ff
    style IT fill:#cfe2ff
    style DB fill:#cfe2ff
    style PR fill:#d1ecf1
    style VB fill:#ffeaa7
    style PUB fill:#d4edda
```

---

## Publishing Strategy

```mermaid
flowchart TD
    A[Code Change] --> B{Branch?}

    B -->|feature/issue/docs| C1[No Publishing<br/>Build Only]
    B -->|develop| C2[No Publishing<br/>Build + Tag]
    B -->|release/X.Y.Z| C3[Test PyPI Publishing<br/>+ Docker UAT]
    B -->|main| C4[No Auto Publishing<br/>Tag Created]
    B -->|hotfix/X.Y.Z| C5[No Auto Publishing<br/>Tag Created]

    C4 --> D[Maintainer Creates<br/>GitHub Release]
    C5 --> D

    D --> E[publish.yml Triggered]
    E --> F[Publish to PyPI<br/>Production]
    E --> G[Docker ghcr.io<br/>Tags: ops, latest, version]

    C3 --> H1[Docker ghcr.io<br/>Tags: uat, version]
    C2 --> H2[Docker ghcr.io<br/>Tags: sit, version]

    F --> I[Production Deployed]
    G --> I

    style C1 fill:#e9ecef
    style C2 fill:#d1ecf1
    style C3 fill:#ffeaa7
    style F fill:#d4edda
    style G fill:#d4edda
    style I fill:#f8d7da
```

---

## Security & Testing Flow

```mermaid
flowchart TD
    A[Code Pushed] --> B{Source?}

    B -->|Internal Repository| C[pr-checks.yml]
    B -->|External Fork| D[pull-request-received.yml]

    C --> C1[Snyk Security Scan<br/>Full Access]
    C --> C2[Unit Tests<br/>With Coverage]
    C --> C3[Integration Tests Available<br/>Post-Merge Only]

    D --> D1[Snyk: Limited<br/>No Secrets]
    D --> D2[Unit Tests Only<br/>No EDL Access]
    D --> D3[No Integration Tests<br/>Security Isolation]

    C1 --> E{Severity?}
    E -->|High on Protected Branch| F1[❌ Fail Build]
    E -->|High on Feature Branch| F2[⚠️ Warn Only]
    E -->|Low/Medium| F3[✅ Pass with Warning]

    F1 --> G[Block Merge]
    F2 --> H[Allow Merge<br/>Developer Notified]
    F3 --> H

    D2 --> I{Tests Pass?}
    I -->|Yes| J[Maintainer Review<br/>Can Run Full Tests]
    I -->|No| K[Block Until Fixed]

    J --> L[If Approved<br/>Merge Follows Normal Flow]

    style C fill:#d1ecf1
    style D fill:#ffeaa7
    style F1 fill:#f8d7da
    style F2 fill:#fff3cd
    style L fill:#d4edda
```

---

## Environment Progression

```mermaid
flowchart LR
    subgraph "Development"
        F[feature/issue/docs]
    end

    subgraph "SIT - System Integration Test"
        D[develop<br/>Version: X.Y.Za#<br/>Docker: sit tag]
    end

    subgraph "UAT - User Acceptance Test"
        R[release/X.Y.Z<br/>Version: X.Y.Zrc#<br/>Test PyPI<br/>Docker: uat tag]
    end

    subgraph "PROD - Production"
        M[main<br/>Version: X.Y.Z<br/>PyPI<br/>Docker: ops, latest]
    end

    F -->|PR Merge| D
    D -->|Create Branch| R
    R -->|PR Merge| M
    M -.GitHub Release.-> P[Published to PyPI]

    style F fill:#e9ecef
    style D fill:#d1ecf1
    style R fill:#ffeaa7
    style M fill:#d4edda
    style P fill:#f8d7da
```

---

## How to Use These Diagrams

1. **View on GitHub:** These diagrams render automatically in GitHub markdown
2. **VS Code:** Install "Markdown Preview Mermaid Support" extension
3. **Online Editor:** Copy/paste to https://mermaid.live/ for editing
4. **Export:** Use mermaid-cli to export as PNG/SVG:
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   mmdc -i CI_CD_ARCHITECTURE_DIAGRAM.md -o diagram.png
   ```

---

## Quick Reference Legend

| Color | Meaning |
|-------|---------|
| 🟢 Green (#d4edda) | Production/Published |
| 🟡 Yellow (#ffeaa7) | UAT/Release Candidate |
| 🔵 Blue (#d1ecf1) | SIT/Development |
| ⚪ Gray (#e9ecef) | Local/Feature Work |
| 🔴 Red (#f8d7da) | Critical/Production Impact |
| 🟠 Orange (#fff3cd) | Warning/Attention Needed |

---

**End of Diagrams**
