import { OpenAI } from 'openai';
import { Ollama } from 'ollama';
import { GoogleGenAI } from '@google/genai';
import Anthropic from '@anthropic-ai/sdk';

export interface GenerationSettings {
  provider: 'ollama' | 'lmstudio' | 'groq' | 'openai' | 'claude' | 'gemini';
  requirement: string;
  endpoints: {
    ollamaEndpoint?: string;
    lmStudioEndpoint?: string;
  };
  keys: {
    groqApiKey?: string;
    openAIApiKey?: string;
    claudeApiKey?: string;
    geminiApiKey?: string;
  };
}

const SYSTEM_PROMPT = `You are an expert QA Engineer. Your task is to generate test cases based on the provided requirements. 
You must output the test cases in a strict Jira tabular/markup format. 
Ensure you cover both Functional and Non-Functional aspects. 
Structure:
h2. Test Case: [Title]
*Functional / Non-Functional:* [Type]
*Description:* [Brief description]

h3. Preconditions
* [Condition 1]

h3. Steps
# [Step 1]
# [Step 2]

h3. Expected Result
* [Result]`;

export async function generateTestCases(settings: GenerationSettings): Promise<string> {
  const { provider, requirement, endpoints, keys } = settings;

  try {
    switch (provider) {
      case 'openai': {
        if (!keys.openAIApiKey) throw new Error('OpenAI API key missing');
        const openai = new OpenAI({ apiKey: keys.openAIApiKey });
        const res = await openai.chat.completions.create({
          model: 'gpt-4o',
          messages: [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: requirement }
          ],
        });
        return res.choices[0].message.content || '';
      }

      case 'groq': {
        if (!keys.groqApiKey) throw new Error('Groq API key missing');
        const groq = new OpenAI({ apiKey: keys.groqApiKey, baseURL: 'https://api.groq.com/openai/v1' });
        const res = await groq.chat.completions.create({
          model: 'mixtral-8x7b-32768',
          messages: [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: requirement }
          ],
        });
        return res.choices[0].message.content || '';
      }

      case 'lmstudio': {
        const baseURL = endpoints.lmStudioEndpoint || 'http://localhost:1234/v1';
        const lmstudio = new OpenAI({ apiKey: 'not-needed', baseURL });
        const res = await lmstudio.chat.completions.create({
          model: 'local-model', // LM studio usually ignores this or uses loaded model
          messages: [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: requirement }
          ],
        });
        return res.choices[0].message.content || '';
      }

      case 'ollama': {
        const host = endpoints.ollamaEndpoint || 'http://127.0.0.1:11434';
        const ollama = new Ollama({ host });
        const res = await ollama.chat({
          model: 'llama3', // Typical default, can be parameterized
          messages: [
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: requirement }
          ],
        });
        return res.message.content || '';
      }

      case 'claude': {
        if (!keys.claudeApiKey) throw new Error('Claude API key missing');
        const anthropic = new Anthropic({ apiKey: keys.claudeApiKey });
        const res = await anthropic.messages.create({
          model: 'claude-3-5-sonnet-20240620',
          max_tokens: 1024,
          system: SYSTEM_PROMPT,
          messages: [
            { role: 'user', content: requirement }
          ],
        });
        return (res.content[0] as any).text || '';
      }

      case 'gemini': {
        if (!keys.geminiApiKey) throw new Error('Gemini API key missing');
        const ai = new GoogleGenAI({ apiKey: keys.geminiApiKey });
        const res = await ai.models.generateContent({
           model: 'gemini-2.5-flash',
           contents: requirement,
           config: { systemInstruction: SYSTEM_PROMPT }
        });
        return res.text || '';
      }

      default:
        throw new Error(\`Unsupported provider: \${provider}\`);
    }
  } catch (error: any) {
    console.error('Generation Error:', error);
    throw new Error(\`Failed to generate with \${provider}: \${error.message}\`);
  }
}
