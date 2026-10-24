# CS4680 — Presentation & Video Guide

## Classroom presentation (~90 seconds, speak naturally)

> Hello everyone. My project is **AI Study Buddy**, a web app designed for college students who need easier explanations and quick practice quizzes.
>
> The problem is that one-size-fits-all explanations can be too complicated, and students do not always know whether they understand a topic.
>
> First, I'll enter “TCP Three-Way Handshake” and select “Computer Science Student.” When I click “Explain Topic,” the app uses my locally running Qwen model through Ollama to create an explanation.
>
> If that explanation is too difficult, I can click “Make it simpler.” The app sends the previous response along with my feedback and generates a revised explanation.
>
> Next, I'll switch to the quiz tab and generate three practice questions. I'll answer them and submit. The app grades my responses and shows why the answers are right or wrong.
>
> This application uses three prompt engineering patterns: **Persona**, making the model act as a CS tutor; **Few-Shot**, providing example answers; and **Iterative Refinement**, improving answers based on feedback.
>
> In the future, I would like to support lecture-note uploads and personalized learning history. Thank you!

### Live demonstration sequence

1. **Before class:** Start Ollama, confirm the model is installed, and start the app. Choose **Local Ollama (FREE)** and confirm the sidebar shows Ollama detected. A local demo can work without internet. Keep any optional OpenAI API keys hidden.
2. Open **Explain a Concept**, enter TCP Three-Way Handshake, click **Explain Topic**.
3. Click **Make it simpler** (shows iterative refinement).
4. Open **Practice Quiz**, generate **3** questions, select answers, click **Submit Answers**.
5. Briefly open **How AI Works** to show the three prompt patterns.
6. Never call Preview mode a live AI demo; it is only a fallback walkthrough.

## Vertical video (<2 minutes)

Suggested format: **1080 × 1920**, 60–90 seconds, screen capture and voice-over, with visible text labels.

| Timing | Show on screen | Voice-over idea |
|---|---|---|
| 0–8s | App name and UI | “Meet AI Study Buddy, my AI-powered tutor.” |
| 8–22s | Topic input and level | “Students type what they want to learn.” |
| 22–40s | AI explanation | “The app creates an explanation matched to their level.” |
| 40–55s | Simplify button and revised answer | “Feedback helps it improve the answer.” |
| 55–75s | Generate quiz and answer | “It also generates a practice quiz and scores it.” |
| 75–90s | Prompt pattern panel + closing | “Persona, few-shot, and iterative refinement power the experience.” |

Record the **real Live AI** experience when possible, not a static mockup. Never record the `.env` file or an API key. Publish the video as an accessible YouTube Short or equivalent, then submit its URL.

## Assignment submission checklist

- [ ] Working app with real Ollama local AI integration (OpenAI optional)
- [ ] Friendly UI and explain/quiz/refine functionality
- [ ] At least two prompt engineering patterns clearly explained
- [ ] Successful classroom live demo
- [ ] Public or instructor-accessible GitHub repo with source/README (no keys)
- [ ] Published short demo video, less than 2 minutes
- [ ] GitHub and video URLs submitted via https://forms.gle/nMHp5owwYidszwt58
- [ ] Due date confirmed in Canvas

**Optional bonus:** Deploy the app to a public hosting platform; note that deployment requires a hosted model/provider and cannot access Ollama running on the student's Mac. This is not needed for the base grade.
