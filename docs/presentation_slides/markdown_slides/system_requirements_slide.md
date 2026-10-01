# SYSTEM REQUIREMENTS

![System Requirements Slide](file:///C:/Users/HAPPY/.gemini/antigravity-ide/brain/61d271b3-e646-4e20-b200-94518da05830/english_system_requirements_slide_1789580727066.png)

---

## Slide Text (100% English - Copy-Paste Ready)

```text
                                SYSTEM REQUIREMENTS

❖ 4.1 HARDWARE REQUIREMENTS
   ➢ CPU: Multi-core (e.g., Ryzen 5th Gen or Intel i5/i7)
   ➢ RAM: 16 GB (Minimum)
   ➢ Storage: SSD, 256 GB or higher
   ➢ Network: High-speed internet connection

❖ 4.2 SOFTWARE REQUIREMENTS
   ➢ Operating System: Windows Server / Windows 10 / Windows 11
   ➢ Programming Language: Python 3.x
   ➢ Machine Learning Models: Stacking Ensemble (XGBoost, LightGBM, CatBoost, Random Forest)
   ➢ Libraries: Pandas, NumPy, scikit-learn, Matplotlib, CatBoost, SHAP, FAISS
   ➢ IDE: Visual Studio Code (VS Code), Google Colab / Streamlit
```

---

### Detailed Component Specifications

| Category | Component | Specification | Description |
| :--- | :--- | :--- | :--- |
| **Hardware** | **CPU** | Multi-core (Ryzen 5th Gen / Intel i5/i7) | Executes multi-threaded parallel predictions across ensemble base models. |
| **Hardware** | **RAM** | 16 GB (Minimum) | Supports SMOTE oversampling matrix computations and SHAP TreeExplainer operations. |
| **Hardware** | **Storage** | SSD, 256 GB or higher | Fast access and loading for serialized trained models (`.pkl`) and vector DB indices. |
| **Hardware** | **Network** | High-speed internet connection | Handles API calls across MCP agents and CIBIL score integration services. |
| **Software** | **Operating System** | Windows Server / Windows 10/11 | Target deployment environment powering local backend server and dashboard. |
| **Software** | **Language** | Python 3.x | Core development language for pipeline, model inference, and RAG retrieval. |
| **Software** | **ML Models** | Stacking Ensemble Classifier | Combines XGBoost, LightGBM, CatBoost, and Random Forest for 96.68% accuracy. |
| **Software** | **Libraries** | Pandas, NumPy, scikit-learn, Matplotlib, CatBoost, SHAP, FAISS | Comprehensive data preprocessing, visualization, explainability, and vector search. |
| **Software** | **IDE** | VS Code / Google Colab / Streamlit | Integrated development environment and application deployment interface. |
