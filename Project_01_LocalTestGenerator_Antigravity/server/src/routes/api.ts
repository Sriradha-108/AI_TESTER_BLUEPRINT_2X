import { Router } from 'express';
import { generateTestCases, GenerationSettings } from '../services/llmService';

const router = Router();

router.post('/test-connection', async (req, res) => {
  const { provider, settings } = req.body;
  // Generic mock logic. In a real scenario, this would do a lightweight API test call.
  // We'll hit the LLM service with a tiny prompt just to verify credentials.
  try {
    const payload: GenerationSettings = {
       provider,
       requirement: "Respond with exactly 'OK'",
       endpoints: {
         ollamaEndpoint: settings.ollamaEndpoint,
         lmStudioEndpoint: settings.lmStudioEndpoint
       },
       keys: {
         groqApiKey: settings.groqApiKey,
         openAIApiKey: settings.openAIApiKey,
         claudeApiKey: settings.claudeApiKey,
         geminiApiKey: settings.geminiApiKey
       }
    };
    await generateTestCases(payload);
    res.json({ success: true, message: \`Successfully connected to \${provider}\` });
  } catch (err: any) {
    res.status(500).json({ success: false, message: err.message });
  }
});

router.post('/generate', async (req, res) => {
  const { requirement, provider, settings } = req.body;
  
  try {
    const payload: GenerationSettings = {
       provider,
       requirement,
       endpoints: {
         ollamaEndpoint: settings.ollamaEndpoint,
         lmStudioEndpoint: settings.lmStudioEndpoint
       },
       keys: {
         groqApiKey: settings.groqApiKey,
         openAIApiKey: settings.openAIApiKey,
         claudeApiKey: settings.claudeApiKey,
         geminiApiKey: settings.geminiApiKey
       }
    };

    const output = await generateTestCases(payload);
    res.json({ success: true, tests: output });
  } catch (err: any) {
    res.status(500).json({ success: false, message: err.message });
  }
});

export { router as apiRouter };
