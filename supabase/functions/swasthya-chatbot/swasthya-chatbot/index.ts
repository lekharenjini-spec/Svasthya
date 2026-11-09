 const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    if (req.method !== "POST") {
      return new Response(
        JSON.stringify({ error: "Method not allowed" }),
        {
          status: 405,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    const { message } = await req.json();

    if (
      typeof message !== "string" ||
      message.trim().length === 0 ||
      message.length > 2000
    ) {
      return new Response(
        JSON.stringify({ error: "Please enter a message (maximum 2000 characters)." }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        },
      );
    }

    const apiKey = Deno.env.get("OPENAI_API_KEY");

    if (!apiKey) {
      throw new Error("The AI service key has not been configured.");
    }

    const aiResponse = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-5.5",
        store: false,
        instructions: `
You are Swasthya Assistant, a helpful assistant inside a healthcare
information app in India.

Reply in the language used by the user, including Malayalam, English,
or Hindi.

You may provide general health information and explain how to use
the Swasthya app.

Never diagnose illnesses, prescribe medicines, or claim to replace
a qualified healthcare professional.

For emergencies, advise the user to contact local emergency services
or go to the nearest emergency department immediately.

Never invent hospital details, ambulance phone numbers, or availability.
Only share contact information verified by the app's database.
Use simple, respectful language.
        `,
        input: message.trim(),
        max_output_tokens: 400,
      }),
    });

    if (!aiResponse.ok) {
      throw new Error("The AI service could not process the request.");
    }

    const data = await aiResponse.json();

    const reply = (data.output ?? [])
      .filter((item: any) => item.type === "message")
      .flatMap((item: any) => item.content ?? [])
      .filter((item: any) => item.type === "output_text")
      .map((item: any) => item.text)
      .join("\n");

    return new Response(
      JSON.stringify({ reply: reply || "Sorry, I could not generate a reply." }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      },
    );
  } catch (error) {
    console.error("Chatbot error:", error);

    return new Response(
      JSON.stringify({ error: "Sorry, the chatbot is temporarily unavailable." }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      },
    );
  }
});