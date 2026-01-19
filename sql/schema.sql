CREATE TABLE prompts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    system_prompt TEXT,
    user_prompt_template TEXT,
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT 0,
    pii_masking BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE prompt_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prompt_id INT,
    alert_hash VARCHAR(64),
    final_prompt TEXT,
    llm_response LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
