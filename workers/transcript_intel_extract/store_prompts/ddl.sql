
-- Enum for prompt categories
create type prompt_category as enum (
    'extraction', 
    'summarization', 
    'analysis', 
    'transformation',
    'classification',
    'other'
);

-- Enum for prompt status
create type prompt_status as enum (
    'draft',
    'active',
    'archived',
    'testing'
);

create table prompts (
    id bigint primary key generated always as identity,
    name text not null unique,
    display_name text not null,  -- User-friendly name for UI
    description text,            -- Brief description for UI listing
    category prompt_category not null,
    status prompt_status default 'draft',
    
    -- Core prompt components
    system_prompt text,
    main_prompt text not null,
    output_format jsonb,
    input_schema jsonb,
    
    -- Additional guidelines and metadata
    guidelines text[],           -- Array of additional guidelines/tips
    example_input text,          -- Example input for reference
    example_output text,         -- Example output for reference
    notes text,                  -- Internal notes/comments
    tags text[],                -- Array of searchable tags
    
    -- UI/UX metadata
    last_edited_by text,        -- User who last edited
    is_favorite boolean default false,
    ui_section_order jsonb,     -- Custom ordering of sections in UI
    
    -- Versioning and timestamps
    version integer default 1,
    created_at timestamp with time zone default timezone('utc'::text, now()),
    updated_at timestamp with time zone default timezone('utc'::text, now()),
    created_by text,
    is_active boolean default true
);

-- Add indexes for common queries
create index idx_prompts_category on prompts(category);
create index idx_prompts_status on prompts(status);
create index idx_prompts_tags on prompts using gin(tags array_ops);