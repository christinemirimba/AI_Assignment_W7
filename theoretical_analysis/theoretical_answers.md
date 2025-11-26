# Part 1: Theoretical Understanding (30%)

## Short Answer Questions

### Q1: Define algorithmic bias and provide two examples of how it manifests in AI systems.

**Algorithmic Bias Definition:**
Algorithmic bias refers to systematic and repeatable errors in AI systems that create unfair outcomes, typically disadvantaging certain groups or individuals. This bias occurs when algorithms make decisions that are systematically prejudiced due to flawed assumptions in the machine learning process, biased training data, or inappropriate algorithm design.

**Two Examples of Manifestation:**

1. **Recruitment and Hiring Systems:** Amazon's AI recruiting tool (2014-2017) demonstrated algorithmic bias by systematically penalizing female candidates. The system was trained on historical hiring data that reflected past gender imbalances in the tech industry, causing it to learn and perpetuate these biases by downgrading resumes that contained words like "women's" (e.g., "women's chess club captain").

2. **Facial Recognition Technology:** Facial recognition systems consistently demonstrate higher error rates for people with darker skin tones, particularly women of color. A study by MIT found that facial recognition systems had error rates up to 34.7% for dark-skinned women compared to 0.8% for light-skinned men, leading to potential misidentification in security and law enforcement applications.

### Q2: Explain the difference between transparency and explainability in AI. Why are both important?

**Transparency:**
Transparency refers to the openness and visibility of AI systems' inner workings, including data sources, algorithm design, decision-making processes, and system architecture. It's about making the "black box" more visible by revealing what components exist, how they're connected, and what inputs/outputs they produce.

**Explainability:**
Explainability focuses on the ability to understand and interpret the AI system's outputs and decisions. It answers questions like "Why did the system make this specific decision?" and "What factors contributed to this outcome?" Explainability translates complex algorithmic processes into human-understandable terms.

**Why Both Are Important:**
- **Transparency** enables accountability, regulatory compliance, and trust in AI systems by allowing stakeholders to understand the system's foundation
- **Explainability** enables users to understand and challenge AI decisions, supports debugging and improvement, and ensures meaningful recourse for affected individuals
- Together, they form the foundation of trustworthy AI and are essential for ethical AI deployment in high-stakes domains like healthcare, criminal justice, and finance

### Q3: How does GDPR (General Data Protection Regulation) impact AI development in the EU?

**Key GDPR Impacts on AI Development:**

1. **Data Processing Restrictions:** GDPR's requirement for explicit consent and lawful basis for processing significantly impacts AI training, requiring developers to ensure data subjects understand how their data will be used in AI systems.

2. **Right to Explanation:** Article 22 of GDPR provides individuals with the right not to be subject to decisions based solely on automated processing, including AI decisions, and requires meaningful information about the logic involved.

3. **Data Minimization and Purpose Limitation:** GDPR's principles require AI developers to collect only necessary data for specified purposes, limiting the use of broad datasets for training models.

4. **Data Subject Rights:** GDPR gives individuals rights to access, rectify, erase, and port their data, which impacts how AI systems handle data lifecycle management and requires robust data governance frameworks.

5. **Privacy by Design:** GDPR mandates privacy considerations from the design phase, requiring AI developers to implement technical measures that ensure data protection by default.

6. **Cross-Border Data Transfer:** GDPR's restrictions on international data transfers impact global AI collaboration and require adequate safeguards for data sharing in AI development.

## Ethical Principles Matching

**Answers:**

A) **Justice** → Fair distribution of AI benefits and risks.
- Justice ensures equitable access to AI benefits while fairly distributing potential harms across all populations.

B) **Non-maleficence** → Ensuring AI does not harm individuals or society.
- This principle mandates that AI systems must be designed to minimize harm and prevent negative consequences.

C) **Autonomy** → Respecting users' right to control their data and decisions.
- Autonomy preserves human agency and self-determination in interactions with AI systems.

D) **Sustainability** → Designing AI to be environmentally friendly.
- This principle addresses the environmental impact of AI systems, including energy consumption and resource utilization.

## Summary

These theoretical foundations demonstrate the complexity of ethical AI development and the need for comprehensive frameworks that address bias, transparency, legal compliance, and fundamental ethical principles. Understanding these concepts is crucial for developing responsible AI systems that serve society equitably while protecting individual rights and dignity.