# AI USAGE DISCLOSURE

## Samsung XR Hackathon — NEUROFRAME-X

**Project Name:** NEUROFRAME-X  
**Project Track:** Action-Aware Video Summarization  
**Team Name:** NEURAL NEXUS  
**Institution:** SRM Institute of Science and Technology, Kattankulathur, Chennai

### Team Members

| Name | Registration Number |
|---|---|
| Aryaman Narain Pandey | RA2411003011237 |
| Maitri Tyagi | RA2411003010652 |
| Vedaang Pratap Singh | RA2411003011530 |
| Mayank Singh | RA2411003010116 |

---

## 1. Purpose of Artificial Intelligence

NEUROFRAME-X is an AI-powered video analysis and action-aware summarization platform.

The system uses machine learning to identify activities in uploaded video footage and organize predictions into structured temporal results.

Its primary objectives are to:

- Analyze video content using pretrained action-recognition models.
- Identify predicted activities across video segments.
- Organize activity predictions into a temporal timeline.
- Select relevant video intervals using application-level highlight-selection logic.
- Generate structured JSON results for downstream processing and visualization.
- Present available analysis results through an interactive web interface.

---

## 2. AI Models Used

### R3D-18 Video Classification Model

**Model:** R3D-18  
**Framework:** PyTorch / Torchvision  
**Pretraining Dataset:** Kinetics-400  
**Purpose:** Video activity classification

R3D-18 is a three-dimensional convolutional neural network designed to process spatial and temporal information from video clips.

NEUROFRAME-X integrates a pretrained R3D-18 model to generate activity predictions from supported Kinetics-400 categories.

The team does not claim to have trained the pretrained model from scratch.

### EPIC-KITCHENS Integration

EPIC-KITCHENS verb–noun recognition was explored during development.

However, the available checkpoint was incompatible with the required separate verb and noun inference heads.

Consequently, **EPIC-KITCHENS verb–noun inference is not operational in the submitted implementation**.

No claim of working EPIC-KITCHENS inference is made.

---

## 3. Generative AI Tools Used During Development

The following AI-assisted development tools were used:

### ChatGPT

ChatGPT assisted with:

- Project planning and technical discussions.
- Software architecture suggestions.
- Code generation and refinement.
- Debugging assistance.
- Documentation preparation.
- Presentation content development.
- Testing guidance.
- Submission preparation.

### Antigravity IDE

Antigravity IDE assisted with:

- Frontend development.
- Backend integration.
- Code modifications.
- Debugging.
- Automated test execution.
- Build verification.
- Repository management.
- Documentation updates.

Generative AI was used as a development aid rather than as a substitute for the project's application-specific implementation.

---

## 4. Team Contributions

The NEURAL NEXUS team was responsible for developing and integrating the NEUROFRAME-X application.

The project combines pretrained machine learning technology with application-specific software components, including:

- Video upload and processing workflows.
- Backend API integration.
- Temporal organization of activity predictions.
- Highlight-selection logic.
- Structured output generation.
- Samsung Student Kit validation.
- Frontend visualization.
- Software testing and submission preparation.

The project does not claim ownership of third-party pretrained models, frameworks, or datasets.

---

## 5. Testing and Validation

The following software checks were reported during development:

| Validation | Reported Result |
|---|---|
| Backend automated tests | 5 passed |
| Frontend production build | Successful |
| Video-processing API request | HTTP 200 |
| Samsung JSON validation | Passed |
| Frontend upload workflow | Verified during development |

These results demonstrate successful execution of selected software functionality and integration checks.

They do not establish comprehensive real-world action-recognition accuracy.

The reported processing test used synthetic video footage rather than a representative real-world benchmark dataset.

---

## 6. Limitations and Transparency

The team acknowledges the following limitations:

1. Activity predictions are limited to the classes supported by the pretrained Kinetics-400 model.
2. Recognition accuracy may vary with video quality, camera movement, viewing angle, and activity type.
3. The current implementation does not provide operational EPIC-KITCHENS verb–noun inference.
4. The existing project walkthrough video is illustrative and does not demonstrate actual live model inference.
5. Automated software tests and JSON validation do not constitute comprehensive evaluation of recognition accuracy.
6. Large pretrained model checkpoints are excluded from the GitHub repository and must be obtained through the configured model-loading process.
7. Generated model predictions should not be interpreted as guaranteed ground truth.

---

## 7. Third-Party Technologies and Attribution

NEUROFRAME-X uses existing software frameworks and pretrained machine learning technology.

These include:

- PyTorch
- Torchvision
- R3D-18
- Kinetics-400
- FastAPI
- React
- Vite

All third-party components remain subject to their respective licenses and terms.

The team acknowledges the contributions of the researchers and developers responsible for these technologies.

---

## 8. AI Usage Declaration

Team NEURAL NEXUS declares that NEUROFRAME-X incorporates pretrained artificial intelligence technology and was developed with assistance from generative AI tools, including ChatGPT and Antigravity IDE.

The disclosure distinguishes existing pretrained models from the team's application-specific software development and integration.

The team acknowledges the limitations of the current implementation and does not claim unsupported model capabilities or unperformed evaluations.

This document is intended to provide transparency regarding the use of artificial intelligence in the NEUROFRAME-X project.

**Project:** NEUROFRAME-X  
**Team:** NEURAL NEXUS  
**Hackathon:** Samsung XR Hackathon

---

**End of AI Usage Disclosure**