# Extreme Harness Engineering for Token Billionaires: 1M LOC, 1B toks/day, 0% human code, 0% human review — Ryan Lopopolo, OpenAI Frontier & Symphony

**Source:** Latent Space  
**Date:** 2026-04-07  
**URL:** https://www.latent.space/p/harness-eng  
**Tier:** 1  

---

We’re proud to release this ahead of Ryan’s keynote at AIE Europe. Hit the bell, get notified when it is live! Attendees: come prepped for Ryan’s AMA with Vibhu after.

Move over, context engineering. Now it’s time for Harness engineering and the age of the token billionaires.

Ryan Lopopolo of OpenAI is leading that charge, recently publishing a lengthy essay on Harness Eng that has become the talk of the town:

fuller discussion between Bret and Ryan
In it, Ryan peeled back the curtains on how the recently announced OpenAI Frontier team have become OpenAI’s top Codex users, running a >1m LOC codebase with 0 human written code and, crucially for the Dark Factory fans, no human REVIEWED code before merge. Ryan is admirably evangelical about this, calling it borderline “negligent” if you aren’t using >1B tokens a day (roughly $2-3k/day in token spend based on market rates and caching assumptions):

search it
Over the past five months, they ran an extreme experiment: building and shipping an internal beta product with zero manually written code. Through the experiment, they adopted a different model of engineering work: when the agent failed, instead of prompting it better or to “try harder,” the team would look at “what capability, context, or structure is missing?”

The result was Symphony, “a ghost library” and reference Elixir implementation (by Alex Kotliarskyi) that sets up a massive system of Codex agents all extensively prompted with the specificity of a proper PRD spec, but without full implementation:

The future starts taking shape as one where coding agents stop being copilots and start becoming real teammates anyone can use and Codex is doubling down on that mission with their Superbowl messaging of “you can just build things”.

Across Codex, internal observability stacks, and the multi-agent orchestration system his team calls Symphony, Ryan has been pushing what happens when you optimize an entire codebase, workflow, and organization around agent legibility instead of human habit.

We sat down with Ryan to dig into how OpenAI’s internal teams actually use Codex, why the real bottleneck in AI-native software development is now human attention rather than tokens, how fast build loops, observability, specs, and skills let agents operate autonomously, why software increasingly needs to be written for the model as much as for the engineer, and how Frontier points toward a future where agents can safely do economically valuable work across the enterprise.

We discuss:

Ryan’s background from Snowflake, Brex, Stripe, and Citadel to OpenAI Frontier Product Exploration, where he works on new product development for deploying agents safely at enterprise scale

The origin of “harness engineering” and the constraint that kicked off the whole experiment: Ryan deliberately refused to write code himself so the agent had to do the job end to end

Building an internal product over five months with zero lines of human-written code, more than a million lines in the repo, and thousands of PRs across multiple Codex model generations

Why early Codex was painfully slow at first, and how the team learned to decompose tasks, build better primitives, and gradually turn the agent into a much faster engineer than any individual human

The obsession with fast build times: why one minute became the upper bound for the inner loop, and how the team repeatedly retooled the build system to keep agents productive

Why humans became the bottleneck, and how Ryan’s team shifted from reviewing code directly to building systems, observability, and context that let agents review, fix, and merge work autonomously

Skills, docs, tests, markdown trackers, and quality scores as ways of encoding engineering taste and non-functional requirements directly into context the agent can use

The shift from predefined scaffolds to reasoning-model-led workflows, where the harness becomes the box and the model chooses how to proceed

Symphony, OpenAI’s internal Elixir-based orchestration layer for spinning up, supervising, reworking, and coordinating large numbers of coding agents across tickets and repos

Why code is increasingly disposable, why worktrees and merge conflicts matter less when agents can resolve them, and what it really means to fully delegate the PR lifecycle

“Ghost libraries”, spec-driven software, and the idea that a coding agent can reproduce complex systems from a high-fidelity specification rather than shared source code

The broader future of Frontier: safely deploying observable, governable agents into enterprises, and building the collaboration, security, and control layers needed for real-world agentic work

Ryan Lopopolo

X: https://x.com/_lopopolo

Linkedin: https://www.linkedin.com/in/ryanlopopolo/

Website: https://hyperbo.la/contact/

## Timestamps

00:00:00 Introduction: Harness Engineering and OpenAI Frontier
00:02:20 Ryan’s background and the “no human-written code” experiment
00:08:48 Humans as the bottleneck: systems thinking, observability, and agent workflows
00:12:24 Skills, scaffolds, and encoding engineering taste into context
00:17:17 What humans still do, what agents already own, and why software must be agent-legible
00:24:27 Delegating the PR lifecycle: worktrees, merge conflicts, and non-functional requirements
00:31:57 Spec-driven software, “ghost libraries,” and the path to Symphony
00:35:20 Symphony: orchestrating large numbers of coding agents
00:43:42 Skill distillation, self-improving workflows, and team-wide learning
00:50:04 CLI design, policy layers, and building token-efficient tools for agents
00:59:43 What current models still struggle with: zero-to-one products and gnarly refactors
01:02:05 Frontier’s vision for enterprise AI deployment
01:08:15 Culture, humor, and teaching agents how the company works
01:12:29 Harness vs. training, Codex model progress, and “you can just do things”
01:15:09 Bellevue, hiring, and OpenAI’s expansion beyond San Francisco

## 

## Transcript

Ryan Lopopolo: I do think that there is an interesting space to explore here with Codex, the harness, as part of building AI products, right? There’s a ton of momentum around getting the models to be good at coding. We’ve seen big leaps in like the task complexity with each incremental model release where if you can figure out how to collapse a product that you’re trying to.

Build a user journey that you’re trying to solve into code. It’s pretty natural to use the Codex Harness to solve that problem for you. It’s done all the wiring and lets you just communicate in prompts. To let the model cook, you have to step back, right? Like you need to take a systems thinking mindset to things and constantly be asking, where is the Asian making mistakes?

Where am I spending my time? How can I not spend that time going forward? And then build confidence in the automation that I’m putting in place. So I have solved this part of the SDLC.

swyx: [00:01:00] All right.

## [00:01:03] Meet Ryan 

swyx: We’re in the studio with Ryan from OpenAI. Welcome.

Ryan Lopopolo: Hi,

swyx: Thanks for visiting San Francisco and thanks for spending some time with us.

Ryan Lopopolo: Yeah, thank you. I’m super excited to be here.

swyx: You wrote a blockbuster article on harness engineering. It’s probably going to be the defining piece of this emerging discipline, huh?

Ryan Lopopolo: Thank you. It is it’s been fun to feel like we’ve defined the discourse in some sense.

swyx: Let’s contextualize a little bit, this first podcast you’ve ever done. Yes. And thank you for spending with us. What is, where is this coming from? What team are you in all that jazz?

Ryan Lopopolo: Sure, sure.

Ryan Lopopolo: I work on Frontier Product Exploration, new product development in the space of OpenAI Frontier, which is our enterprise platform for deploying agents safely at scale, with good governance in any business. And. The role of VMI team has been to figure out novel ways to deploy our models into package and products that we can sell as solutions to enterprises.

swyx: And you have a background, I’ll just squeeze it in there. Snowflake, brick, [00:02:00] stripe, citadel.

Ryan Lopopolo: Yes. Yes. Same. Any kind of customer

swyx: entire life. Yes. The exact kind of customer that you want to,

Vibhu: so I’ll say, I was actually, I didn’t expect the background when I looked at your Twitter, I’m seeing the opposite.

Stuff like this. So you’ve got the mindset of like full send AI, coding stuff about slop, like buckling in your laptop on your Waymo’s. Yes. And then I look at your profile, I’m like, oh, you’re just like, you’re in the other end too. Oh, perfect. Makes perfect.

Ryan Lopopolo: I it’s quite fun to be AI maximalist if you’re gonna live that persona.

Open eye is the place to do it. And it’s

swyx: token is what you say.

Ryan Lopopolo: Yeah. Certainly helps that we have no rate limits internally. And I can go, like you said, full send at this stay.

swyx: Yeah. Yeah. So the Frontier, and you’re a special team within O Frontier.

Ryan Lopopolo: We had been given some space to cook, which has been super, super exciting.

## [00:02:47] Zero Code Experiment

Ryan Lopopolo: And this is why I started with kind of a out there constraint to not write any of the code myself. I was figuring if we’re trying to make agents that can be deployed into end to enterprises, they should be [00:03:00] able to do all the things that I do. And having worked with these coding models, these coding harnesses over 6, 7, 8 months, I do feel like the models are there enough, the harnesses are there enough where they’re isomorphic to me in capability and the ability to do the job.

So starting with this constraint of I can’t write the code meant that the only way I could do my job was to get the agent to do my job.

Vibhu: And like a, just a bit of background before that. This is basically the article. So what you guys did is five months of working on an internal tool, zero lines of code over a mi, a million lines of code in the total code base.

You say it was cenex, more like it was cenex faster than you would’ve. If you had done it by end. So

Ryan Lopopolo: yeah, that

Vibhu: was the mindset going into this, right?

Ryan Lopopolo: That’s right.

## [00:03:46] Model Upgrades Lessons

Ryan Lopopolo: Started with some of the very first versions of Codex CLI, with the Codex Mini model, which was obviously much less capable than the ones we have today.

Which was also a very good constraint, right? Quite a visceral feeling to ask the [00:04:00] model to build you a product feature. And it just not being able to assemble the pieces together.

Which kind of defined one of the mindsets we had for going into this, which is whenever the model just cannot, you always pop open at the task, double click into it, and build smaller building blocks that then you can reassemble into the broader objective.

And it was quite painful to do this. Honestly, the first month and a half was. 10 times slower than I would be. But because we paid that cost, we ended up getting to something much more productive than any one engineer could be because we built the tools, the assembly station for the agent to do the whole thing.

## [00:04:43] Model Generations, Build Systems & Background Shells

Ryan Lopopolo: But yeah, so onward to G BT 5, 5, 1, 5, 2, 5, 3, 5 4. To go through all these model generations and see their kind of corks and different working styles also meant we had to adapt the code base to change things up when the model was revved. [00:05:00] One interesting thing here is five two, the Codex harness at the time did not have background shells in it, which means we were able to rely on blocking scripts to perform long horizon work.

But with five, three and background shells, it became less patient, less willing to block. So we had to retool the entire build system to complete in under a minute and. This is not a thing I would expect to be able to do in a code base where people have opinions. But because the only goal was to make the Asian productive over the course of a week, we went from a bespoke make file build to Basil, to turbo to nx and just left it there because builds were fast at that point.

swyx: Interesting. Talk more about Turbo TenX. That’s interesting ‘cause that’s the other direction that other people have been doing.

Ryan Lopopolo: Ultimately I have. Not a lot of experience with actual frontend repo architecture.

swyx: You’re talking that Jessica built the sky. So I’m like, I know the NX team. I know Turbo from Jared [00:06:00] Palmer.

And I’m like, yeah, that’s an interesting comparison.

## [00:06:02] One Minute Build Loop

Ryan Lopopolo: The hill we were climbing right, was make it fast.

swyx: Is there a micro front end involved? Is it how how complex react

Ryan Lopopolo: electron base single app sort of thing

swyx: And must be under a minute. That’s an interesting limitation. I’m actually not super familiar with the background shelf stuff.

Probably was talked about in the fight three release.

Ryan Lopopolo: BA basically means that codex is able to spawn commands in the background and then go continue to work while it waits for them to finish. So it can spawn an expensive build and then continue reviewing the code, for example.

swyx: Yeah.

Ryan Lopopolo: And this helps it be more time efficient for the user invoking the harness.

swyx: And I guess and just to really nail this, like what does one minute matter? Like why not five, okay, good. We want no. We

Ryan Lopopolo: want the inner loop to be as fast as possible. Okay. One minute was just a nice round number and we were able to hit it.

swyx: And if it doesn’t complete, it kills it or some something,

Ryan Lopopolo: No.

We just take that as a signal that we need to stop what we’re doing, double click, decompose a build graph a bit to get us to high back under so that we [00:07:00] can able the agent continue to operate.

swyx: It’s almost like you’re, it’s like a ratchet. It’s like you’re forcing build time discipline, because if you don’t, it’ll just grow and grow.

That’s right. And you mentioned that my current, like the software I work on currently is at 12 minutes. It sucks.

Ryan Lopopolo: This has been my experience with platform teams in the past, where you have an envelope of acceptable build times and you let it go up to breach and then you spend two, three weeks to bring it back down to the lower end of the average low bed stop.

But because tokens are so cheap Yeah. And we’re so insanely parallel with the model, we can just constantly be gardening this thing to make sure that we maintain these in variants, which means. There’s way less dispersion in the code and the SDLC, which means we can simplify in a way and rely on a lot more in variance as we write the software.

## [00:07:45] Observability, Traces & Local Dev Stack

Vibhu: Lovely.

## [00:07:46] Humans Are Bottleneck

Vibhu: You mentioned in your article, like humans became the bottleneck, right? You kicked off as a team of three people. You’re putting out a million line of code, like 1500 prs, basically. What’s the mindset there? So as much as code is disposable, you’re doing a lot of review. A lot [00:08:00] of the article talks about how you wanna rephrase everything is prompting everything, is what the agent can’t see.

It’s kind of garbage, right? You shouldn’t have it in there. So what’s like the high level of how you went about building it, and then how you address okay, humans are just PR review. Like how is human in the loop for this?

Ryan Lopopolo: We’ve moved beyond even the humans reviewing the code as well.

## [00:08:19] Human Review, PR Automation & Agent Code Review

Ryan Lopopolo: Most of the human review is post merge at this point.

But post, post merge, that’s not even reviewed. That’s just

swyx: Oh, let’s just make ourselves happy by You

Ryan Lopopolo: haven’t used fundamentally. The model is trivially paralyzable, right? As many GPUs and tokens as I am willing to spend, I can have capacity to work with my hood base.

The only fundamentally scarce thing is the synchronous human attention of my team. There’s only so many hours in the day we have to eat lunch. I would like to sleep, although it’s quite difficult to, stop poking the machine because it makes me want to feed it. You have to step back, right?

Like you need to take a systems thinking mindset to things and [00:09:00] constantly be asking where is the agent making mistakes? Where am I spending my time? How can I not spend that time going forward? And then build confidence in the automation that I’m putting in place. So I have solved this part of the SDLC, and usually what that has looked like is like we started needing to pay very close attention to the code because the agent did not have the right building blocks to produce.

Modular software that decomposed appropriately that was reliable and observable and actually accrued a working front end in these things, right?

## [00:09:35] Observability First Setup

Ryan Lopopolo: So in order to not spend all of our time sitting in front of a terminal at most, doing one or two things at a time, invested in giving the model that observability, which is that that graph in the post here.

swyx: Yeah. Let’s walk through this traces and which existed first

Ryan Lopopolo: we started with just the app and the whole rest of it. From vector through to all these login metrics, APIs was, I dunno, half an [00:10:00] afternoon of my time. We have intentionally chosen very high level fast developer tools. There’s a ton of great stuff out there now.

We use me a bunch, which makes it trivial to pull down all these go written Victoria Stack binaries in our local development. Tiny little bit of python glue to spin all these up. And off you go. One neat thing here is we have tried to invert things as much as possible, which is instead of setting up an environment to spawn the coding agent into, instead we spawn the coding agent, like that’s the entry point.

It’s just Codex. And then we give Codex via skills and scripts the ability to boot the stack if it chooses to, and then tell it how to set some end variables. So the app and local Devrel points at this stack that it has chosen to spin up. And this I think is like the fundamental difference between reasoning models and the four ones and four ohs of the past, where these models could not think so you had to put them in [00:11:00] boxes with a predefined set of state transitions.

Whereas here we have the model, the harness be the whole box. And give it a bunch of options for how to proceed with enough context for it to make intelligent choices. So

Vibhu: sales, so like a lot of that is around scaffolding, right? Yes. Previous agents, you would define a scaffold. It would operate in that.

Lube, try again. That’s pivoted off from when we’ve had reasoning models. They’re seeming to perform better when you don’t have a scaffold, right? That’s right.

## [00:11:28] Docs Skills Guardrails

Vibhu: And you go into like niches here too, like your SPEC MD and like having a very short agent MG Agent md.

swyx: Yes. Yes.

Vibhu: Yeah. So you even lay out what it is here, but I like

swyx: the table contents.

Vibhu: Yeah.

swyx: Like stuff like this, it really helps guide people because everyone’s trying to do this.

Ryan Lopopolo: This structure also makes it super cheap to put new content into the repository to steer both the humans and the agents.

swyx: You, you reinvented skills, right?

Vibhu: One big agents and

swyx: skills from first princip holds

Ryan Lopopolo: all skills did not exist when we started doing this.

Vibhu: You have a short [00:12:00] one 100 line overall table of contents and then you have little skills, right? Core beliefs, MD tech tracker. Yeah. Yeah. The scale is over

Ryan Lopopolo: The tech jet tracker and the quality score are pretty interesting because this is basically a tiny little scaffold, like a markdown table, which is a hook for Codex to review all the business logic that we have defined in the app, assess how it matches all these documented guardrails and propose follow up work for itself.

Before beads and all these ticketing systems, we were just tracking follow up work as notes in a markdown file, which, we could spa an agent on Aron to burn down. There’s this really neat thing that like the models fundamentally crave text. So a lot of what we have done here is figure out ways to inject text

swyx: into

Ryan Lopopolo: the system right when we get a page, because we’re missing a timeout, for example.

I can just add Codex in Slack on that page and say, I’m gonna fix this by adding a timeout. Please update our reliability documentation. To require that all network calls have [00:13:00] timeouts. So I have not only made a point in time fix, but also like durably encoded this process knowledge around what good looks like.

swyx: Yeah.

Ryan Lopopolo: And we give that to the root coding agent as it goes and does the thing. But you can also use that to distill tests out of, or a code review agent, which is pointed at the same things to narrow the acceptable universe of the code that’s produced.

swyx: I think one of the concerns I have with that kind of stuff is you think you’re making the right call by making, it’s persisted for all time across everything.

Yes. But then you didn’t think about the exceptions that you need to make, right? And that you have to roll it back.

Vibhu: Part of it is

swyx: also sometimes it can follow your s instructions too.

Vibhu: It’s somewhat a skill, right? So it determines when it uses the tools, right? Like it’s not like it’ll run outta every call.

It’ll determine when it wants to check quality score, right?

Ryan Lopopolo: Yeah. And we do in the prompts we give these agents, allow them to push back,

## [00:13:51] Agent Code Review Rules

Ryan Lopopolo: When we first started adding code review agents to the pr, it would be Codex, CLI. Locally writes the change, pushes up a PR on [00:14:00] those PR synchronizations of review agent fires.

It posts a comment. We instruct Codex that it has to at least acknowledge and respond to that feedback. And initially the Codex driving the code author was willing to be bullied by the PR reviewer, which meant you could end up in a situation where things were not converging. So yeah, we had to,

swyx: he’s just a thrash.

Ryan Lopopolo: We had to add more optionality to the prompts on both of these things, right? The reviewer agents were instructed to bias toward merging the thing to not surface anything greater than a P two in priority. We didn’t really define P two, but we gave it, you

swyx: did define P two.

Ryan Lopopolo: We gave it a framework within which to score its output

swyx: and then greater than P zero is worse, right?

Yes. P two is very good.

Ryan Lopopolo: P zero is you will mute the code place if

swyx: you merch this

Ryan Lopopolo: thing, right?

swyx: Yeah.

Ryan Lopopolo: But also on the code authoring agent side, we also gave it the flexibility to either defer or push back against review feedback, right? This happens all the time, right? Like I happen to notice something and leave a code review, [00:15:00] which.

Could blow up the scope by a factor of two. I usually don’t mean for that to be addressed Exactly. In the moment. It’s more of an FYI file it to the backlog, pick it up in the next fix it week sort of thing. And without the context that this is permissible, the coding agents are gonna bias toward what they do, which is following instructions.

swyx: Yeah.

## [00:15:19] Autonomous Merging Flow

swyx: I do wanted to check in on a couple things, right? Sure. All the coding review agent, it can merge autonomously. I think that’s something that a lot of people aren’t comfortable with. And you have a list here of how much agents do they do Product code and tests, CI configuration and release tooling, internal Devrel tools, documentation eval, harness review, comments, scripts that manage the repository itself, production dashboard definition files, like everything.

Yes. And so they’re just all churning at the same time, is there like a record that, that any human on the team pulls to stop everything

Ryan Lopopolo: Because we are building a native application here. We’re not doing continuous deploy. So there’s still a human in the loop for cutting the release branch.

I see. We require a blessed [00:16:00] human approved smoke test of the app before we promote it to distribution, these sort of things.

swyx: So you’re working on the app, you’re not building like infrastructure where you have like nines of reliability, that kinda stuff?

Ryan Lopopolo: That’s correct. That’s correct. Okay. And also like full recognition here that all of this activity took in a completely greenfield repository.

There’s. Should be no script that this applies generally to

swyx: this is a production thing, you’re gonna ship

Ryan Lopopolo: to

swyx: customers. Of course. Yeah, of course. So this is real

Vibhu: And like one of the things there is, you mentioned you started this as a repo from scratch. The onboarding first month or so was pretty, it was like working backwards, right?

Yeah. And then you had to work with the system and now you’re at that point where you know, you’re very autonomous. I’m curious like, okay, so what, how human in the loop is it? So what are the bottlenecks that you wish you could still automate? And part of that is also like, where do you see the model trajectory improving and offloading more human in the loop?

We just got 5.4. It’s a really good,

Ryan Lopopolo: fantastic model, by the way.

Vibhu: Yeah. Yeah. It’s the first one that’s merged. Top tier coding. So it’s codex level coding and reasoning. So general reasoning both in one model. So

Ryan Lopopolo: and

Vibhu: computer [00:17:00] use vision.

Ryan Lopopolo: Now we now with five four, I can just have Codex write the blog post, whereas for this one I had to balance between chat.

swyx: Oh, I need to, I might be out of a job. Oh my God.

Ryan Lopopolo: Oh,

swyx: I know. You just gave me an idea for a completely AI newsletter that five four could do. Yeah, I get it Now.

Ryan Lopopolo: This sort of thing is just one example of closing the loop, right? Like the dashboard thing you mentioned. We have Codex authoring the Js ON, for the Grafana dashboards and publishing them and also responding to the pages, which means when it gets the page, it knows exactly which dashboards are defined and what alerts.

What alert was triggered by which exact log in the code base. ‘cause all of this stuff is collated together.

swyx: It has to own everything.

Yes. Yeah. Yeah.

Ryan Lopopolo: And it means that if we have an outage that did not result in a page. It has the existing set of dashboards available to it. It has the existing set of metrics and logs and can figure out where the gaps in the dashboard are or [00:18:00] in the underlying metrics and fix them in one go.

In the same way, you would have a full stack engineer be able to drive a feature from the backend all the way to the front end.

Vibhu: So it, it seems like a lot of the work you guys had to do was you as a small team are fully working for a way that the model wants the software to be written. It’s like less human legible for better. Code legibility, agent legibility. How do you think that affects broader teams? So one at OpenAI, do liaison, like this is how software should be written. Like I can imagine, say you join a new team with this methodology, this mindset there’s ways that, teams do code review, teams write code, like teams are structured and a lot of it is for human legibility.

So should we all swap? Like how does this play back one broader into OpenAI and then like broader into the software engineering, right? Is it like teams that pick this up will it’s pretty drastic, right? You have to make a pretty big switch. Should they just full send Yeah.

Ryan Lopopolo: The mindset is very much that I’m removed from the process, right? I can’t really have deep code level opinions about [00:19:00] things. It’s as if I’m. Group tech leading a 500 person organization.

Vibhu: Yeah.

Ryan Lopopolo: Like it’s not appropriate for me to be in the weeds on every pr. This is why that post merge code review thing is like a good analog here, right?

Like I have some representative sample of the code as it is written, and I have to use that to infer what the teams are struggling with, where they could use help, where they’re already moving quickly and I can pivot my focus elsewhere.

Vibhu: Yeah.

Ryan Lopopolo: So I don’t really have too many opinions around the code as it is written.

I do, however, have a command based class, which is used to have repeatable chunks of business logic that comes with tracing and metrics and observability for free. And the thing to focus on is not how that business logic is structured, but that it uses this primitive ‘cause I know that’s gonna give leverage by default.

Vibhu: Yeah.

Ryan Lopopolo: Yeah, back to that sort of systems stinking,

Vibhu: and you have part of that in your blog post, enforcing architecture and ta taste how you set boundaries for what’s used. There’s also a section on redefining [00:20:00] engineering and stuff, but yeah, it’s just, it’s interesting to hear,

Ryan Lopopolo: and as the models have gotten better, they have gotten better at proposing these abstractions to unblock themselves, which again, lets me move higher and higher up the stack to look deeper into the future on what ultimately blocked the team from shipping.

swyx: Yeah. You mentioned so you, this is primarily a, it is like a 1 million line of code base electron app. But it manages its own services as well, so it’s like a backend for front end type thing.

Ryan Lopopolo: We do have a backend in there, but that’s hosted in the cloud.

Yeah. This sort of structure is actually within the separate main and render processes

Within the

swyx: electric.

That’s just how electronic works.

Ryan Lopopolo: Yeah, of course. So have also treated like. MVC style decomposition with the same level of rigor, which has been very fun.

swyx: I have a fun pun. This is a tangent, NVC is model view controller. Any sort of full stack web Devrel knows that.

But my AI native version of this is Model view Claw, the clause the harness.

Ryan Lopopolo: That’s right. That’s right. I do think that there is an interesting space to [00:21:00] explore here with Codex, the harness as part of building AI products, right? There’s a ton of momentum around getting the models to be good at coding.

We’ve seen big leaps in like the task complexity with each incremental model release where if you can figure out how to collapse a product that you’re trying to build, a user journey that you’re trying to solve into code, it’s pretty natural to use the Codex Harness to solve that problem for you. It’s done all the wiring and lets you just communicate and prompts to let the model cook.

Yeah. It’s been very fun. And there’s also a very engineering legible way of increasing capabil. It’s fantastic, right? Yeah. Just give you, just give the model scripts, the same scripts you would already build for yourself.

swyx: Yeah.

Yeah. So for listeners, this is Ryan saying that software engineering or coding against will eat knowledge work like the non-coding parts that you would normally think.

Oh, you have to build a separate agent for it. No, start a coding agent and go out from there. Which open Claw has like it’s pie Underhood.

Ryan Lopopolo: [00:22:00] Yes.

Vibhu: Basically define your task in code. Everything is a coding

swyx: agent by the way. Since I brought it up, it’s probably the only place we bring it up. Is any open claw usage from you?

Any?

Ryan Lopopolo: No. No. Not for me. I don’t have any spare Mac Minis rattling around my house.

swyx: You can afford it? No. I just, I’m curious if it’s changed anything in opening eye yet, but it’s probably early days. And then the other, the other thing I, I wanna pull on here is like you mentioned ticketing systems and you mentioned prs and I’m wondering if both those things have to go away or be reinvented for this kind of coding.

So the git itself and is like very hostile to multi-agent.

Ryan Lopopolo: Yeah. We make very heavy use of work trees.

swyx: But like even then, like I just did a, dropped a podcast yesterday with Cursors saying, and they said they’re getting rid of work trees ‘cause it still has too many merge conflicts.

It’s still un too un unintuitive. But go ahead.

Ryan Lopopolo: The models are really great at resolving merge conflicts. Yeah. And to get to a state where I’m not synchronously in the loop in my terminal, I almost don’t care that there are merge

swyx: with disposable.

[00:23:00] Yeah.

Ryan Lopopolo: We invoke a dollar land skill and that coaches codex to push the PR Wait for human and agent reviewers Wait for CI to be green.

Fix the flakes if there are any merged upstream. If the PR comes into conflict, wait for everything to pass. Put it in the merge queue. Deal with flakes until it’s in Maine. End. This is what it means to delegate fully, right? This is in a, very large model re probably a significant tax on humans to get PRS merged, but the agent is more than capable of doing this and I really don’t have to think about it other than keep my laptop open.

swyx: Yeah. I used to be much more of a control freak, but now I’m like, yeah, actually you could do a better job of this than me. Yeah. With the right context. Yes.

## [00:23:47] Encoding Requirements

swyx: Anything else in harness in general? Just this piece, I just wanna make sure we,

Ryan Lopopolo: I think one thing that I maybe didn’t make super clear in the article that I heard on Twitter as an interesting, that’s respond [00:24:00]

swyx: to them.

What’s the chatter and then what’s your response?

Ryan Lopopolo: Ultimately, all the things that we have encoded in docs and tests and review agents and all these things are ways to put all the non-functional requirements of building high scale, high quality, reliable software into a space that prompt injects the agent.

We either write it down as docs, we add links where the error messages tell how to do the right thing. So the whole meta of the thing is to basically tease out of the heads of all the engineers on my team, what they think good looks like, what they would do by default, or what they would coach a new hire on the team to do to get things to merch.

And that’s why we pay attention to all the mistakes, mistakes that the agent makes, right? This is code being written that is misaligned with some as yet not written down, non-functional requirement.

swyx: Sorry, what? Did the online people misunderstand or

Ryan Lopopolo: No,

swyx: what

you

Ryan Lopopolo: responded to? Somebody just literally said that.

I was like, oh yeah,

swyx: okay,

Ryan Lopopolo: This is the [00:25:00] thing. This is what I’ve been doing. Oh, you

swyx: agree? Yeah. I see. Interesting.

Ryan Lopopolo: One other neat thing, which I did totally did not expect is folks were just. Taking the link to the article and giving it to pi or Codex and say, make my repo this,

Vibhu: you achi a whole recursion.

Ryan Lopopolo: And it was wildly effective. Really? It was wildly effective. No

Vibhu: way. It just actually is something I tried with five, four yesterday. I didn’t have time. Last time I was like out speaking of something, and this is one of my things, I was like, okay, I have this article. Can we just scaffold out what it would be like to run this?

And I, I did it first as that and then I was like, okay, let me take another little side repo and say okay, if I was to fully automate this like this because I haven’t written a line of code, it’s

Ryan Lopopolo: like over full, set

Vibhu: it right. The side thing I’m doing of voice. TTS I’m just like, slobbing out, whatever.

It’s nothing production. I’m like, how would I make this like this? And it’s actually like a really good way. It’s like a good way to learn what could be changed, what could be like, it’s just a good analyzing, right? You give it all the codes, you give it all the context, you give it the article and it walks you through it very well.

That’s right. That’s right.

## [00:25:57] Inlining Dependencies

## [00:25:57] Dependencies Going Away & Brett Taylor’s Response

swyx: I guess one more thing before we go to Symphony is I wanted to cover [00:26:00] Brett Taylor’s response. We had him on the show. He is your chairman, which is wild. Yeah. That he’s reading your articles as well and like getting engaged in it. He says software dependencies are going away.

Basically they can just be like vendored. Yes. Response.

Ryan Lopopolo: A

swyx: hundred percent. A hundred percent agree. You still pro qr, you still pay Datadog. You still pay Temporal. Thank you.

Ryan Lopopolo: Yep. The level of complexity of the dependencies that we can internalize is, I would say low, medium right now. Just based on model capability.

What does the,

swyx: what is medium?

Ryan Lopopolo: I would say like a. A couple thousand line dependency is a thing that we could in-house No problem. Call in an afternoon of time. One neat thing about it is like probably most of that code you don’t even need. Like by in-house and abstraction, you can strip away all the generic parts of it and only focus on what you need to enable the specific thing.

Yes. You’re building,

swyx: I’ve been calling this the end of bullshit plugins.

Ryan Lopopolo: Yeah.

swyx: Because there’s so much when I published an open source thing, I want to accept everything, be liberal. I want to accept, this is post’s law, but that means there’s so much bloat. Yes. There’s so much overhead.

Ryan Lopopolo: One other neat thing about [00:27:00] this too is when we deploy Codex Security on the repo, it is able to deeply review and change. The internalized dependencies in a much lower friction way than it would be to like, push patches upstream, wait for them to be released, pull them down, make sure that’s compatible with all the transitive I have in my repo and things like that.

So it’s also much lower friction to internalize some of these things if code is free. ‘cause the tokens are cheap sort of thing.

swyx: Yeah. Yeah. I think like the only argument I have against this is basically scale testing, which obviously the larger pieces of software like Linux, MySQL, he calls up even the Datadog and Temporals and then maybe security testing where Yes.

Classically, I think, is it linis tos, it said security open source is the best disinfectant.

Ryan Lopopolo: Many eyes.

swyx: Many eyes. And if inline your dependencies and code them up, you’re gonna have to relearn mistakes from other people that Yep.

Ryan Lopopolo: Yep. And to internalize that dependency, you’re back to zero and you have to start.

Reassembling all those bits and pieces to Yeah. Have [00:28:00] high confidence in the code as it is written. Yeah.

Vibhu: Even part of the first intro of this, you basically mentioned like everything was written by codex, including internal tooling, right? So internal tooling, like when you’re visualizing what’s going on it’s writing it for itself.

swyx: Yeah. I’m built internal tools way I now, and like I just show them off and they’re like, how long did you spend? And I didn’t spend any time. I just prompted it,

Ryan Lopopolo: very funny story here.

swyx: Yeah, go ahead.

Ryan Lopopolo: We had deployed our app to the first dozen users internally had some performance issues, so we asked them to export a trace for us get a tar ball, gave it to our on-call engineer, and he did a fantastic job of working with Codex to build this beautiful local Devrel tool, next JS app, the drag and drop the tar ball in, and it visualizes the entire trace.

It’s fantastic. Took an afternoon, but none of this was necessary. Because you could just spin up codex and give it the tar ball and ask the same thing and get the response immediately. So in a way, optimizing for human [00:29:00] legibility of that debugging process was wrong. It kept him in the loop unnecessarily when instead he could have just like Codex cooked for five minutes and gotten this same.

swyx: Yeah, you verify your instincts here of this is how we used to do it. Or this is how I would have used to solve it.

Ryan Lopopolo: Yeah. In this local observability stack. Like sure, you can de deploy Yeager to visualize the traces, but I wouldn’t expect to be looking at the traces in the first place because I’m not gonna write the code to fix them.

swyx: Yeah. So basically there needs to be like this kind of house stack and owning the whole loop. I think that is very well established. And it sounds like you might be like sharing more about that in the future, right?

Ryan Lopopolo: Yeah. I think we’re excited to do

## [00:29:36] Ghost Libraries Specs

## [00:29:36] Ghost Libraries & Distributing Software as Specs

Ryan Lopopolo: We’re gonna talk about Symphony in a little bit, but like the way we distribute it as a spec, which I think folks are calling Ghost Libraries on Twitter.

This is like a such a cool name. It does mean it becomes much cheaper to share software with the world, right? You define a spec, how you could build your own specifying as much as is required for a coding agent to reassemble it [00:30:00] locally. The flow here is very cool. Like we have taken. All the scaffolding that has existed in our proprietary repo spun up a new one.

Ask Codex with our repo as a reference. Write the spec. We tell it. Spin up a team ox spawn a disconnected codex to implement the spec. Wait for it to be done. Spawn another codex and another team ox to review the spec com or review the implementation compared to upstream and update the spec so it diverges less.

And then you just loop over and over Ralph style until you get a spec that is with high fidelity able to reproduce the system as it is. It’s fantastic.

Vibhu: And you’re basically, you’re not really adding any of your human bias in there, right? That’s correct. A lot of times people write a spec and be like, okay, I think it should be done this way, and you’ll riff on something.

And it’s no, the agent could have just handled it like you’re still scaffolding in a sense, right? I want it done this way. It can determine its spec better.

swyx: That’s right. That’s right. Part of me it, I’m, I’ve been working a lot on evals recently, and part of me is wondering if [00:31:00] an agent can produce a spec that it cannot solve.

Is it always capable of things that he can imagine or can you imagine things that it is impossible to do?

Ryan Lopopolo: I think with Symphony, we, there’s like this there’s this axis where you have things that are easier, hard, or established or new, right? And I think things that are hard and new is still something that the models need humans.

Yeah. Drive.

swyx: Yeah. Yeah.

Ryan Lopopolo: But I think those other quadrants are largely salt. Given the right scaffold and the right thing that’s gonna drive the agent to completion,

swyx: it’s crazy that it solved,

Ryan Lopopolo: but it means that the humans, the ones with limited time and attention get to work on the hardest stuff, like the problems where it’s pure white space out in front. Or like the deepest refactorings where you don’t know what the proper shape of the interfaces are. And this is where I wanna spend my time. ‘cause it lets me set up for the next level of scale.

swyx: Yeah. Yeah. Amazing. Let’s introduce Symphony.

I think we’ve been mentioning it every now and then. Elixir. Interesting option.

Ryan Lopopolo: Yeah.

swyx: Yeah. I’m not,

Ryan Lopopolo: again, like the [00:32:00] elixir manifestation here is just a derivative. Is it a model

swyx: chosen? Yeah.

Ryan Lopopolo: Yeah. Yeah. And it chose that because the process supervision and the gen servers are super amenable to the type of process orchestration that we’re doing here.

You are essentially spinning up little Damons for every task that is in execution and driving it to completion, which. Means the mall gets a ton of stuff for free by using Elixir and the Beam.

swyx: I had to go do a crash course in Beam and Elixir, and I think most people are not operating at that scale of concurrency where you need that.

But it is a good mental model for Resum ability and all those things. And these are things I care about. But tell me the story, the origin story of Symphony. What do you use it for? Is this, how did it form maybe any abandoned paths that you didn’t take?

## [00:32:46] Terminal Free Orchestration

## [00:32:46] Symphony: Removing Humans from the Loop

Ryan Lopopolo: At the end of December we were at about three and a half PRS per engineer per day.

This was before five two came out in the beginning of January. Everyone gets back from holiday with five two and no other work [00:33:00] on the repository. We were up in the five to 10 PRS per day per engineer. And I don’t know about y’all, but like it’s very taxing to constantly be switching like that. Like I was pretty tapped out at the end of the day, again, where are the humans spending their time? They’re spending their time context switching between all these active tmox pains to drive the agent forward.

swyx: Yeah. No way. Yeah.

Ryan Lopopolo: So let’s again, build something to remove ourselves from the loop. And this is what frantic sprinted adapt here to find a way to remove the need for the human to sit in front of their terminal.

So a lot of experimentation with Devrel boxes and, automatically spinning up agents, like it seems like a fantastic end state here, where my life is beach. I open live twice a day and say yes no to these things. Yeah. And this is again, a super, super interesting framing for how the work is done.

Because I become more latency and sensitive. I have [00:34:00] way less attachment to the code as it is written. Like I’ve had close to zero investment in the actual authorship experience. So if it’s garbage. I can just throw it away and not care too much about it. In Symphony, there’s this like rework state where once the PR is proposed and it’s escalated to the human for review, it should be a cheap review.

It is either mergeable or it is not. And if it’s not, you move it to rework. The elixir service will completely trash the entire work tree NPR and start it again from scratch. Okay. And this is that opportunity again to say, why was it trash right? What did the agent do that was

swyx: bad. Yeah.

Ryan Lopopolo: Fix that before moving the ticket to

swyx: end

Ryan Lopopolo: of progress again.

swyx: Yeah. Why is this not in codex app? I guess this, you guys are ahead of Codex app,

Ryan Lopopolo: yeah, so the way the team has been working is basically to be as AI pilled as possible and spread ahead. And a lot of the things we have worked on have fallen out [00:35:00] into a lot of the products that we have.

Like we were in deep consultation with the Codex team to. Have the Codex app be a thing that exists, right? To have skills be a thing that Codex is able to use. So we didn’t have to roll our own to put automations into the product. So all of our automatic refactoring agents didn’t have to be these hand rolled control loops.

It has been really fantastic to be, in a way, un anchored to the product development of Frontier and Codex and just very quickly try to figure out what works and then later find the scalable thing that can be deployed widely. It’s been a very fun way to operate. It’s certainly chaotic. I have lost track very often of what the actual state of the code looks like.

‘cause I’m not in the loop. There was. One point where we had wired playwright directly up to the Electron app. With MCPM CCPs, I’m pretty bearish on because the harness forcibly injects all those tokens in the [00:36:00] context, and I don’t really get a say over it. They mess with auto compaction. The agent can forget how to use the tool.

There’s probably only what three calls in playwright that I actually ever want to use. So I pay the cost for a ton of things. Somebody vibed a local Damon that boots playwright and exposes a tiny little shim CLI to drive it. And I had zero idea that this had occurred because to me, I run Codex and it’s able to, it’s oh, it’s better.

Yeah. Like no knowledge of this at all. Uhhuh.

## [00:36:30] Multi Human Chaos

Ryan Lopopolo: So we have had like in human space to spend a lot of time doing synchronous knowledge sharing. We have a daily standup that’s 45 minutes long because we almost have to. Fan out the understanding of the current state.

swyx: Yeah, I was gonna say this is good for a single human multi-agent, but multi human, multi-agent is a whole like po like explosion of stuff.

Ryan Lopopolo: Yeah. And that this is fundamentally why we have such a rigid, like 10,000 [00:37:00] engineer level architecture in the app because we have to find ways to carve up the space so people are not trampling on each other.

swyx: Sorry, I don’t get the 10,000 thing. Did I miss that?

Ryan Lopopolo: The structure of the repository is like 500 NPM packages.

It’s like architecture to the excess for what you would consider, I think normal for a seven person team. But if every person is actually like 10 to 50. Then the like numbers on being super, super deep into decomposition and sharding and like proper interface boundaries make a lot more sense.

swyx: Yeah. To me, that’s why I talked about Microfund ends and I, an anex is from that world, but Cool. It is just coming back to, to, to this I dunno if you have other, thoughts on. Orchestrating so much work coin going through this. Is this enough? Is this like any aha moments?

Vibhu: It’ll be interesting to see like where, okay, so right now you pick linear as your issue tracker, right?

swyx: Or it’s like a is it actually linear? This is actually linear.

## [00:37:55] Linear vs Slack Workflow

Vibhu: Oh, that’s linear. It’s linear.

swyx: Oh I never looked at

Vibhu: video. The demo video I had to download to [00:38:00] run.

swyx: So I, because I’m a Slack maxie, but Yeah, linear. Linear is also really good. Yes,

Ryan Lopopolo: we do make a good use of Slack. We we fire off codex to do all these lotion, elasticity, fix ups, the things that like sync that knowledge into the repository.

It’s super cheap. Yeah.

swyx: Yeah.

Ryan Lopopolo: Just do it in Codex.

swyx: My biggest plug is OpenAI needs to build Slack. You need to own Slack. Build yours. Turn this into Slack.

Ryan Lopopolo: I did read about it. You

swyx: did?

Ryan Lopopolo: Yeah.

## [00:38:25] Collaboration Tools for Agents

Ryan Lopopolo: I would say that if we think that we want these agents to do economically valuable work, which is like this is the mission, right?

We want AI to be deployed widely, to do economically valuable work, then we need to find ways for them to naturally collaborate with humans, which means collaboration tooling, I think, is an interesting space to explore.

swyx: Yeah, totally. Yeah. GitHub, slack, linear.

Vibhu: Yeah, that was my thing. Okay, where do we see right now Codex has started Codex Model, then CLI, now there’s an app, app can let me shoot off multiple Codex is in parallel, but there’s no great team collaboration for Codex.

And it [00:39:00] seems like your team had some say into what comes out, right? So you talked to ‘em, codex kind of was a thing. From there, if you guys are on the bound, what stuff that like, you might not focus on, but what do you expect other people to be building, right? So people that are like five x 50 Xing.

Should you build stuff that’s like very niche for your workflow, for your team? Should it be more general so other people can adopt? Is there a niche there? ‘Cause part of it is just okay, is everything just internal tooling? Do we have everything our own way? Like the way our team operates has our own ways that we like to communicate or is there a broader way to do it?

Is it something like a issue tracker? Just thoughts if you wanna riff on that.

## [00:39:35] Standardizing Skills and Code

Ryan Lopopolo: I think TBD we have not figured this out in a general way. I do think that there is leverage to be had in making the code and the processes as much the same as possible. If you think that code is context, code is prompts, it’s better from the agent behavior perspective to be able to look in a package in directory X, Y, Z, and it not to have to page so [00:40:00] deeply into directory if you C, because they have the same structure, use the same language, they have the same patterns internally.

And that same like leverage comes from aligning on a single set of skills that you’re pouring every engineer’s taste into to make sure that the agent is effective. So like in our code base, we have, I think, six skills. That’s it. And if some part of the software development loop is not being covered, our first attempt is to encode it in one of the existing setup skills, which means that we can change the agent behavior.

Yeah. More cheaply than changing the human driver behavior.

swyx: Yeah.

## [00:40:39] Self Improvement via Logs

swyx: Have you ever, have you experimented with agents changing their own behavior?

Ryan Lopopolo: We do.

swyx: Yeah. Or parent agent changing a subagents, behavior or something like that.

Ryan Lopopolo: We have some bits for skill distillation. So for example, there’s one neat thing you can do with Codex, which is just point it at its own session logs to ask it to tell you how you can use [00:41:00] the tool pedal better.

swyx: It’s like introspection

Ryan Lopopolo: or ask it to do things. I use

Vibhu: this session better. What skills should I

swyx: high? I like the modification of, you can do, just do things to you can just ask agent to do things.

Ryan Lopopolo: Yeah. You can just codex things. This is like a, this is like a silly emoji that we have, right? You can just codex things, you can just prompt things.

It’s really glorious future we live in, but okay, you can do that one-on-one. But we’re actually slurping these up for the entire team into blob storage and. Running agent loops over them every day to figure out where as a team can we do better and how do we reflect that back into the repositories?

Yes, though everybody benefits from everybody else’s behavior for free. Same for like PR comments, right? These are all feedback. That means the code as written, deviated from what was good, a PR comment, a failed build. These are all signals that mean at some point the agent was missing context. We gotta figure out how to

swyx: Yeah.

Ryan Lopopolo: Slurp it up and put it back in the reboot.

swyx: By the way, I do this exactly right. I used to, when I use cloud code for [00:42:00] knowledge work, cloud cowork is like a nice product, right? Yes. In I think you would agree. I always have it tell me what do I do better next time? And that’s the meta programming reflection thing.

So I almost think like you have six reflection extraction levels in symphony and almost like the zero of layer. So the six levels are PO policy, configuration, coordination, execution, integration, observability. We’ve talked about a couple of these, but the zero layer is like the, okay, are we working well?

Can we improve how we work? Yes. Can I modify my own workflow without MD or something? I don’t know.

Ryan Lopopolo: Yeah, of course. Yeah, of course you can. Like this thing is also able to cut its own tickets ‘cause we give it full access.

Yeah. Make it a ticket to have it cut. Tickets you can.

Put in the ticket that you expect it to file as on follow up work,

swyx: like Yeah. Self-modifying. Yeah.

Ryan Lopopolo: Yeah.

## [00:42:44] Tool Access and CLI First

Ryan Lopopolo: Put, don’t put the agent in a box. Give the agent full accessibility over it. Domain.

swyx: I had a mental reaction when you said don’t put the agent in a box. So I think you should put it in a box. Like it’s just that you’re giving the box everything it needs.

Ryan Lopopolo: Yeah. Context and tools.

swyx: But we’re like, as developers, we’re used to calling [00:43:00] out to different systems, but here you use the open source things like the Prometheus, whatever, and you run it locally so that you can have the full loop. I assume.

Ryan Lopopolo: Yep.

Vibhu: I think like

Ryan Lopopolo: another, you wanna minimize cloud, cloud dependencies.

Vibhu: You also want to make sure that you think about what the agent has access to. What does it see? Does it go back into the loop, like from the most basic sense of you let it see its own like calls, traces it can determine where it went wrong. But are you feeding that back in? So you know, just the most basic level of you wanna see exactly what’s input output, like does the agent have access to.

What is being outputted, right? It can self-improve a lot of these things. It’s all

Ryan Lopopolo: text, right? My job is to figure out ways to funnel text from one agent to the other.

swyx: It’s so strange like way back at the start of this whole AI wave Andre was like, English is the hottest day programming language.

It’s here, it’s just Yeah. The feature as well.

Vibhu: A lot of, okay. Like a lot of software, a lot of stuff. There’s a gui, it’s made for the human. We’re seeing the evolution of CLI for everything, right? All tools have CLIs. Your agents can use [00:44:00] them well, do we get good vision? Do we get good little sandboxes?

Like right now? It’s a really effective way, right? Models love to use tools. They love the best. They love to read through text. So slap a CLI let it go loose. That works for everything.

Ryan Lopopolo: It does. Yeah. Yeah.

## [00:44:14] UI Perception and Rasterizing

Ryan Lopopolo: We’ve also been adapting nont, textual things to that shape in order to improve model behavior in some ways, right?

We want the agent to be able to see the UI agents do not perceive visually in the same way that we do. They don’t see a red box, they see red box button, right? They see these things in latent space. So if we want, Hey, yeah, I do. We have

swyx: a ding if that goes off every time. Alien space

Ryan Lopopolo: ding.

Anyway if we wanna actually make it see the layout, it’s almost easier to rasterize that image to ask EOR and feed it in to the agent. Ha. And there’s no reason you can’t do both, right? To like further refine how the model perceives the object it’s [00:45:00] manipulating.

swyx: Cool. Could we, you wanna talk about a couple more of these layers that might bear more introspection or that you have personal passion for?

## [00:45:07] Coordination Layer with Elixir

Ryan Lopopolo: I will say that the coordination layer here was a really tricky piece to get right.

swyx: Let’s do it. Yep. I’m all about that. And this is Temporal core.

Ryan Lopopolo: This is where when we turn the spec into Elixir, where like the model takes a shortcut, right? Like it’s oh, I have all these primitives that I can make use of in this lovely runtime that has native process supervision.

Which is I think, a neat way to have taken the spec and made it more choices achievable by making choices that naturally map

swyx: Yeah.

Ryan Lopopolo: To the domain, right? In the same way that like you would prefer to have a TypeScript model repo if you are doing full stack web development, right? Because the ability to share types across the front end and backend reduces a lot of complexity.

And because

swyx: that’s what graph kill used to be.

Ryan Lopopolo: That’s right. And

swyx: I don’t know if it’s still alive, but

Ryan Lopopolo: [00:46:00] no humans in the loop here. So like my own personal ability to write or not write elixir. Doesn’t really have to bias us away from using the right tool for the job. It is just wild.

swyx: Love it. I love it.

Yeah. I wonder if any languages struggle more than others because of this? I feel like everyone has their own abstractions. That would make sense. But maybe it might be slower, it might be more faulty where like you’d have to just kick the server every now and then. I, I don’t know. I think observability layer is really well understood.

Integration layer, CP is dead. I think all these just like a really interesting hierarchy to travel up and down. It’s common language for people working on the system to understand

Ryan Lopopolo: The policy stuff is really cool, right? Yeah. You don’t really have to build a bunch of code to make sure the system wait for the, to pass

swyx: it’s institutional knowledge.

Ryan Lopopolo: Yeah. You just give it the G-H-C-L-I with some text that say CI has to pass. It makes the maintenance of these systems a lot easier.

## [00:46:57] Agent Friendly CLI Output

swyx: Do you think that CLI maintainers need to be [00:47:00] do anything special for agents or just as is? It’s good because like I don’t think when people made the G GitHub, CLI, they anticipated this happening.

Ryan Lopopolo: That’s correct. The GH CLI is fantastic. It’s great super industry.

swyx: Everyone go try GH repo create GH pull and then pull request number, right? GH HPR, like 1 53, whatever. And then it like pulls

Ryan Lopopolo: basically my only interaction with the GitHub web UI at this point is GH PR view dash web.

Exactly. Glance

swyx: at the diff

Ryan Lopopolo: and be like Sure thing. Send it. Yeah. But the CLI are nice ‘cause they’re super token efficient and they can be made more token efficient really easily. Like I’m sure you all have seen like I go to build Kite or Jenkins and I could just get this massive wall of build output.

And in order to unblock the humans, your developer productivity team is almost certainly gonna write some code that parses the actual exception out of the build logs and sticks it in a sticky note at the top of the page. And you basically [00:48:00] want CLI to be structured in a similar way, right? You’re gonna want to patch dash silent to prettier because the agent doesn’t care that every file was already formatted.

Just wants to know it’s either formatted or not. So it can then go run a right command. Similarly, like in our PNPM distributed script runner, when we had one, when you do dash recursive, like it produces a absolute mountain of text. But all of that is for passing. Test suites. So we ended up wrapping all of this in another script

swyx: to suppress the,

Ryan Lopopolo: which you can vibe the channel only output the failing parts of the tests.

swyx: You make a pipe errors versus the standard, standard out. I don’t know. Okay. Whatever. Too much thinking have to do that. The CII used to maintain SCLI for my company and yeah, this is like core, very core to my heart. But you’re vibing my job.

Ryan Lopopolo: That’s right.

swyx: Cool. Any other things?

This is a long spec. [00:49:00] I appreciate that. It’s got a lot of strong opinions in here. Any other things that we should highlight? I think obviously you can spend the whole day going through some of these, but I do think that some of these have a lot of care or some of this you might wanna tell people, Hey, take this, but, make it your own.

## [00:49:15] Blueprint Spec and Guardrails

Ryan Lopopolo: Fundamentally, software is made more flexible when it’s able to adapt to the environment in which it is deployed, which means that things like linear or GitHub even are specified within the spec, but not required pieces of it. There’s like a more platonic ideal of the thing that you could swap in like Jira or Bitbucket, for example.

But being able to tightly specify things like the ID formats or how the Ralph Loop works for the individual agents. Basically means you can get up and running with a fully specified system quickly that you then evolve later on. I think we never intended for this to be a static spec that you can [00:50:00] never change.

It’s more like a blueprint to get something worth a starting point up and running.

swyx: Yeah.

Ryan Lopopolo: For you then to vibe later to your heart’s content,

swyx: you have like code and scripts in here where it’s oh, I think this is a really good prompt. It’s just a very long prompt.

Ryan Lopopolo: Fundamentally, the agents are good at following instructions, so give them instructions.

And it will, improve the reliability of the result. We, much like the way we use Symphony, we don’t want folks to have to monitor the agent as it is vibing the system into existence. So being very opinionated

Very strict around what these success criteria are means that our deployment success rate goes up. Yeah. It means we don’t have to get tickets on this thing.

Vibhu: Think it all goes back to that like code to disposable, right? Like early on when you had CLI or you’d kick off a Codex run, it would take two hours. You would wanna monitor okay, I’m in the workflow of just using one.

I don’t want it to go down the wrong path. I’ll cut it off and, just shoot off four, like that was my favorite thing of the Codex app, right? Yeah. Just Forex it like, [00:51:00] it’s okay. One of them will probably be right, one of them might be better. Stop overthinking it. Like my first example was probably like deep research.

When you put out deep research and I’d ask it something like, I asked it something about LLM, it thought it was legal something and spent an hour, came back with a report completely off the rails. And I was like, okay, I gotta monitor this thing a bit. No don’t monitor it. Just you want to build it so it’s that it, it goes the right way.

And you don’t wanna, you don’t wanna sit there and babysit, right? You don’t want to babysit your agents

Ryan Lopopolo: with that deep research query that you made. Looking at the bad result, you probably figured out you needed to tweak your prompt Yeah. A bit, right? That’s that guardrail that you fed back into the code base for the task, your prompt to further align the agent’s execution.

Same sort of concept supply there too.

swyx: When you talk, how are the customers feeling

Ryan Lopopolo: for Symphony? I think we have none, right? This is a thing we have put out into the

swyx: world. Symphony’s internal, right? As long as you are happy, you are the customer. That’s right. Just, what’s the external view?

## [00:51:53] Trust Building with PR Videos

Ryan Lopopolo: I’d say folks are very excited about this way of distributing software and ideas in [00:52:00] cheap ways. For us as users, it has again, pushed the productivity five x, which means I think there’s something here that’s like a durable pattern around removing the human from the loop and figuring out ways to trust the output.

The video that is shared here

swyx: Yeah.

Ryan Lopopolo: Is the same sort of video we would expect the coding agent to attach to the pr.

swyx: Yeah.

Ryan Lopopolo: That is created. Yeah. That’s part of building trust in this system and that’s, to me, like fundamentally what has been cool about building this is it more closely pushes that persona of the agent working with you to be like a teammate.

I don’t shoulder surf you like for the tickets that you work on during the week. I would never think that I would want to do that.

swyx: Yeah.

Ryan Lopopolo: I wouldn’t want a screen recording of your entire session in Cursor or Claude code. I would expect you to do what you think you need to do to convince me that the code is good and [00:53:00] mergeable

swyx: Yeah.

Ryan Lopopolo: And compress that full trajectory in a way that is legible to me. The reviewer.

swyx: Yeah.

Ryan Lopopolo: It’s Stu. And you can just do that because Codex will absolutely sling some f you can just around. It’s great.

swyx: Oh, F FM P is the og like God, CLI.

Ryan Lopopolo: Yeah.

swyx: Swiss Army Chainsaw. I used to say. There’s a SaaS, micro SaaS that’s called it in every flag in FFM Peg.

Ryan Lopopolo: Oh, for sure.

swyx: You know what I mean? For sure. Just host it as a service, put a UI on it. People who don’t know FM Peg will pay for it.

Ryan Lopopolo: When we were first experimenting with this, it was a wild feeling to be at the computer with just like windows just popping up all over the place and getting captured and files appearing on my desktop, like very much felt like the future to have a thing controlling my computer for like actual productive use.

Like I’m just there

swyx: keeping it. Like awake, jiggling the mouse every once in a while. That’s what some office workers do. So they buy a mouse jiggler. That’s right.

## [00:53:59] Spark vs Reasoning Models

Vibhu: One thing I [00:54:00] wanted to ask, so okay, as stuff is so CO is disposable is saying shoot off a budget of agents. One question is okay, are you always like a extra high thinking guy?

And where do you see Spark? So 5.3 Spark, there’s a lot of me wanting to make quick changes. I’m not gonna open up a id, I’m not gonna do anything. But I will say, okay, fix this little thing, change a line, change a color. Spark is great for that, but am I still a bottleneck? Like, why don’t I just let that go back?

I’m like, just riff on that. Is there,

Ryan Lopopolo: spark is such a different model compared to the. The extra high level reasoning that you get in these, five Yeah. To clear for people.

swyx: It is a different model, different architecture, different, like it doesn’t support

Ryan Lopopolo: it, it just, it’s incredibly fast smaller model.

I have not quite figured out how to use it yet. To be honest, I use faster. I was adapting it to the same sorts of tasks I would use X high reasoning for. Yeah. I, and it would blow through three compactions before writing a line of code.

Vibhu: And that’s another big thing with 5.4 right.

Million co context.

Ryan Lopopolo: Yes, it’s

Vibhu: fantastic. Which is huge [00:55:00] ingenix, right? Like you can just run for longer before you have to compact. The more tokens you can spend on a task before compacting, like the better you’ll do.

Ryan Lopopolo: That’s right. That’s right. I’m not sure how to deploy spark. I think your intuition is right, that it’s very great for spiking out prototypes, exploring ideas quickly, doing those documentation updates.

It is fantastic for us in taking that feedback and transforming it into a lint. Where we already have good infrastructure for ES links in the code base these sorts of things it’s great at and it allows us to unblock quickly doing those like anti-fragile healing tasks in the code base.

swyx: Yeah, that makes sense.

## [00:55:38] What Models Can’t Do Yet

swyx: So you are push, you guys are pushing models to the freaking limit.

## [00:55:41] Current Model Limitations

swyx: What can current models not do well yet?

Ryan Lopopolo: They’re definitely not there on being able to go from new product idea to prototype single

swyx: one shot.

Ryan Lopopolo: This is where I find I spend a lot of time steering is translating end state of a mock for a net new [00:56:00] thing, right?

Think no existing screens into product that is playable with. Similarly, while this has gotten better with each model release, like the gnarliest refactorings are the ones that I spend my most time with, right? The ones where I’m interrupting the most, the ones where I am. Now double clicking to build tooling to help decompose monoliths and things like that.

This is a thing I only expect to get better, right? Over the course of a month, we went from the low complexity tasks to like low complexity and big tasks in both these directions. So this is what it means to not bet against the model, right? You should expect that it is going to push itself out into these higher and higher complexity spaces.

Yeah. So the things we do are robust to that. It just basically means I’ll be able to spend my time elsewhere and figure out what the next bottleneck is.

Vibhu: I do think it’s also a bit of a different type of task, right? Codex is really good at codebase understanding, working with code bases. But companies like Lovable bolt, repli, they solve a very different [00:57:00] problem.

Scaffold of zero to one, right? Idea of a product. And it’s there, there are people working on that and models are also pushing like step function changes there. It’s just different than the software engineering agents today, right?

Ryan Lopopolo: Like I said, the model is isomorphic to myself.

The only thing that’s different is figuring out how to get what’s in here into context for the model and for these white space sort of projects. I, myself, I’m just not good at it. Which means that often over the agent trajectory, I realize the bits that we’re missing, which is why I find I need to have this synchronous interaction.

And I expect with the right harness, with the right scaffold, that’s able to tease that outta me or refine the possible space, right? To be super opinionated around the frameworks that are deployed or to put a template in place, right? These are ways to give the model. All those non-functional requirements, that extra context to acre on and avoid that wide dispersion of possible outcomes.

swyx: Thank [00:58:00] you for that.

## [00:58:00] Frontier Enterprise Platform

swyx: I wanted to talk a little bit about Frontier.

Ryan Lopopolo: Yeah, sure.

swyx: Overall you guys announced it maybe like a month ago. And there’s a few charts in here and it’s basic like your enterprise offering is what I view it. Is there one product or is there many,

Ryan Lopopolo: I can’t speak to the full product roadmap here, but what I can say is that Frontier is the platform by which we want to do AI transformation of every enterprise and from big to small.

And the way we want to do that is by making it easy to deploy highly observable, safe, controlled, identifiable agents into the workplace. We want it to work with your company native. I am stack. We want it to plug into the security tooling that you have. Oh, we want it to be able to plug into the workspace tools that you used,

swyx: so you’re just gonna be stripping specs, right?

Ryan Lopopolo: We expect that there will be some harness things there. Agents, SDK is a core [00:59:00] part of this to enable both startup builders as well as enterprise builders to have a works by default harness that is able to use all the best features of our models from the Shell tool down to the Codex Harness with file attachments and containers and all these other things that we know go into building highly reliable, complex agents.

We wanna make that great and we wanna make it easy to compose these things together in ways that are safe, for example, right? Like the G-P-T-O-S-S safeguard model. For example. One thing that’s really cool about it is it ships. The ability to interface with a safety spec. Safety specs are things that are bespoke to enterprises.

We owe it to these folks to figure out ways for them to instrument the agents in their enterprise to avoid exfiltration in the ways they specifically care about, to know about their internal company, code names, these sorts of things. So providing the right hooks to make the [01:00:00] platform customizable, but also, mostly working by default for folks is the space we are trying to explore here.

swyx: Yeah. And this is the snowflakes of the world just need this, right? Yes. Your Brexit of the world stripes. Yeah, it makes sense.

## [01:00:11] Dashboards and Data Agents

swyx: I was gonna go back to your, I think the demo videos that you guys had was pretty illustrative. It’s like also to me an example of very large scale agent management.

Yes. Like you give people a control dashboard that if you play, if you like, play any one of these like multiple agent things, you can di dig down to the individual instant and see what’s going on.

Ryan Lopopolo: Yes, of course.

swyx: But who’s the user Is it let’s it like the CEO, the CTO, ccio, something like that.

Ryan Lopopolo: At least with my personal opinion here, the buyer that we’re trying to build product for here is one and employees who are making productive use of these agents, right?

That’s gonna be whatever surfaces they appear in the connectors they have access to, things like that. Something like this dashboard is for it. Your GRC and governments folks, your AI innovation office, your security [01:01:00] team, right? The stakeholders in your company that are responsible for successfully deploying into.

The spaces where your employees work, as well as doing so in a safe way that is consistent with all the regulatory requirements that you have and customer attestations and things like that. So it is a iceberg beneath the actual end. It’s,

swyx: yeah you jump every, I guess layer in the UI is like going down the layer of extraction in terms of the agent, right?

Yep. Yeah. Yeah. I think it’s good.

Ryan Lopopolo: Yeah. The ability to dive deep into the individual agent trajectory level is gonna be super powerful.

Not only for from like a security perspective, but also from like someone who is accountable for developing skills. One thing that was interesting that we also blogged about shipping was an internal data agent, which uses a lot of the frontier technology in order to make our data ontology accessible to the agent and things like that to understand.

What’s actually in the data [01:02:00] warehouse?

swyx: Yeah. Seman layer Yes. Type things. Yes. I was briefly part of the, that, that world is it salt? I don’t know. It’s actually really hard for humans to agree on what revenue is. Yes.

Ryan Lopopolo: Yes.

swyx: What is an active user?

Ryan Lopopolo: There’s what, five data scientists in the company that have defined this Golden.

swyx: They, yeah. And no. And there’s also internal politics. Yes. As to attribution of I’m marketing, I’m responsible for this much, and sales is responsible for this much, and they all add up to more than a hundred. And I’m like you guys have different definitions.

Vibhu: Yeah. And if you’re a startup, everything is a RR,

swyx: So I think that’s cool.

Oh, you guys blog about this. Okay. I didn’t see this. Yeah. Is this the same thing? I don’t know. This is what you’re referring to? Yes. Okay. We’ll send people to read this. This is our data.

Vibhu: Him this one.

swyx: Yeah. I don’t know if you’re you have any highlights? I

Vibhu: No. In general from the playlist.

Yeah. A lot of good things to read.

swyx: Yeah. Yeah. Lot, lots of homework for people. No, but like data as the feedback layer, you need to solve this first in order to have the products feedback loop closed. That’s right. So for the agents to understand and this is not something that humans have not solved.

This like, and

Ryan Lopopolo: this is [01:03:00] how you build artists that do more than coding, right? Yeah.

swyx: Yeah.

Ryan Lopopolo: To actually understand how you operate the business.

swyx: Yeah.

Ryan Lopopolo: You have to understand what revenue is, what your customer segments are. Yeah. What your product lines are.

## [01:03:13] Company Context and Memes

Ryan Lopopolo: Like one thing that’s in looping back to the code base that we described here for harnessing, one thing that’s in core beliefs.md is who’s on the team, what product we’re building, who our end customers are.

Who our pilot customers are, what the full vision of what we want to achieve over the next 12 months is these are all bits of context that inform how we would go about building the software. Oh my God. So we have to give it to the agent too.

Vibhu: I’m guessing that stuff is like pretty dynamic and it changes over time too, right?

Like part of it was, it’s not just a big spec. You have it as one of the things and it will iterate.

Ryan Lopopolo: One, one thing that I think is gonna break your mind even more is we have skills for how to properly generate deep fried memes and have Ji culture [01:04:00] and Slack. Because with the Slack Chachi PT app that you’re able to use in Codex, like I can get the agent to shit post on my behalf.

Just, it’s part of humor.

swyx: Theme humor. Humor is part of EGI. Is it funny? It is pretty good, yeah. Okay. Yeah,

Ryan Lopopolo: it’s pretty good at making

swyx: Deep, it’s a lot of I think humor is like a really hard intelligence test, right? It’s like you have to get a lot of context into like very few words.

This is why make references

Ryan Lopopolo: is why five four is such a big uplift for our it’s the me. Yeah, for sure. Yeah. Yeah.

swyx: It’s very cool.

Vibhu: So five, four can two post. So that’s what we take over here.

Ryan Lopopolo: Yeah. Maybe maybe when y’all are done here today, ask Codex to go over your coding agent sessions and to roast you.

swyx: Love it. I’ll give it a shot. Give a shot. Coming back to the final point I wanted to make is, yeah I think that there, there are multiple other, like you guys are working on this, but this is a pattern that every other company out there should adopt. Yes. Regardless of whether or not they work with you.

To me, this is I saw this, I was like, fuck, [01:05:00] every company needs this. This

is

swyx: multiple billions.

Ryan Lopopolo: This is what it takes to get

swyx: Yeah.

Ryan Lopopolo: People to Yes. Yeah. Actually realize the benefits. Yes. And distribute.

swyx: And it’s, it, I think it sounds boring to people like, oh, it’s for safeguards and whatever, but I think you to handle agents at scale like you are envisioning here I don’t know if it’s like a real screenshot, like a demo, but this is what you need.

This is, or my original sort of view of what Temporal was supposed to be that you, you built this dashboard and you basically have every long running process in the company Yes. In one dashboard and that’s it. That’s right.

Vibhu: Yeah. I think it’s pretty customized towards every enterprise, right?

Like you care about different things.

swyx: There’s a lot of customization, but there’ll be multiple unicorns just doing this as a service. I don’t know. I’m like very frontier field, if you can tell. Amazing. But it, it only clicked ‘cause obviously this came out first, then Harness eng, then symphony and only clicked for me that like, this is actually the thing you shipped to do that.

Ryan Lopopolo: Yeah. Yeah. There’s a set of building blocks here that we assembled into these agents [01:06:00] and the building blocks themselves are part of the product, right? Yeah. The ability to steer revoke authorization if a model becomes misaligned, like all of this is accessible through Frontier. And there’s gonna be a bunch of stakeholders in the company that have the things they need to see in the platform Yeah.

To get to. Yes. So we’ll build all of those in the frontier so that we can actually do the widespread the planet. Yeah. That’s the fun part.

swyx: Yeah. I’m also calling back to there’s this like levels of EGI I don’t know if Opening Eye is still talking about this, but they used to talk about five levels of EGI and one of it was like, oh, it’s like an intern coding software patient.

At some point it was AI organization and this is it. That’s right. This is level four or five. I can’t remember which, which level, but it’s somewhere along that path. Was this.

Ryan Lopopolo: You know how I mentioned that my team is having fun sprinting ahead here. And we do this thing where we’re collecting all the agent trajectories from Codex to slurp them up and distill them.

This is what it means to build our team [01:07:00] level knowledge base, happen to reflect it back into the code base. But it doesn’t have to be that way. And it doesn’t have to be bound to just codex. I want Chacha BT to also learn our meaning culture and also the product we are building and how so that when I go ask it, it also has the full context of the way I do my work and I’m super excited for Frontier to enable this.

swyx: Yeah. Amazing.

## [01:07:21] Harness vs Training Tension

swyx: What are the model people say when they see you do this? Like you have a lot of feedback, obviously you have a lot of usage, you have a lot of trajectories and don’t, I don’t imagine a lot of it’s useful to them, but some of it is,

Vibhu: you have this too, you deploy a billion tokens of intelligence a day and this was, this was at the beginning of 2096.

You’re Yeah. Cooking.

Ryan Lopopolo: Yeah, there’s this fundamental tension, which I think you have talked about between whether or not we invest deeper into the harness or we invest deeper into the training process to get the model to do more of this by default. Yeah, and I think success for the way we are [01:08:00] operating here means the model gets better taste because we can point the way there and none of the things we have built actively degrade Asian performance.

‘cause really all they’re doing is running tests and like running tests is a good part of what it means to write reliable software. If we were building an entire separate rust scaffold around Codex to restrict its output, that I think would be like additional harness that would be prone to being scrapped.

But yeah. Yeah. If instead we can build all the guardrails in a way that’s just native to the output that Codex is already producing, which is code, I think. No friction with how the model continues to advance, but also like just good engineering and that’s the whole point.

swyx: Yeah. So I’ve had similar discussions with research scientists where the RL equivalent is on policy versus off policy.

Yeah. And you’re basically saying that you should build an on policy harness, which is already within distribution and you [01:09:00] modify from there. But if you build it off policy, it’s not that useful.

Ryan Lopopolo: That’s right.

swyx: Super cool. Any, anybody thoughts, any things that we haven’t covered that we should get it, get out there?

## [01:09:08] Closing Thoughts & OpenAI Hiring

Ryan Lopopolo: Just I’ve been super excited to benefit from all the cooking that the Codex team has been doing. Yes. They absolutely ship relentlessly. This is one of our core engineering values, ship relentlessly, and they, the team there embodies it. To extreme degree, yeah, I have five three and then Spark and five four come out within what feels like a month is just a phenomenally fast.

swyx: It’s exactly a month ago it’s five three and yesterday was five four. Yeah. I mean it’s, do we have every month now is five five next? Exactly.

Ryan Lopopolo: I can’t say that the poll markets would be very upset.

swyx: I think it’s interesting that it’s also correlated with the growth. They announced that it’s 2 million users, but like almost don’t care about Codex anymore.

This is it, this is the gay man. It’s like coding cool, soft like knowledge work.

Ryan Lopopolo: That’s right. That’s right. This is the thing to chase after. Yeah. And this is one of things that my team is excited to support,

swyx: get the whole like [01:10:00] self-hosted harness thing working, which you have done and like the rest of us are trying to figure out how to catch up, but then do things.

You That’s right. With you

Vibhu: do things.

swyx: That’s right. You can just do things. That’s the line for the episode.

Vibhu: That’s it. Any other call to actions. You’re based in Seattle, your team, I’m guessing. New Bellevue office.

Ryan Lopopolo: New Bellevue office. We just had the grand opening yesterday as of the recording date which was fantastic.

Beautiful buildings. Super excitedly part of the Bellevue Community building the future in Washington. And I would say that there is lots of work to be done in order to successfully serve enterprise customers here in Frontier. We are certainly hiring and if you haven’t tried the Codex app yet, please give it a download.

We just passed 2 million weekly active users growing at a phenomenally fast rate, 25% week over week. Come join us.

swyx: Yes. And I think that’s an interesting no. My, my final observation opening is a very San Francisco centric company. I know people who have been. [01:11:00] Who turned down the job or didn’t get the job ‘cause they didn’t want to move to sf and now they just don’t have a choice.

You have to open the London, you have to open the Seattle. And I wonder if that’s gonna be a shift in the culture, obviously you can’t say, but

Ryan Lopopolo: I was one of the first engineering hires out of our Seattle office, so Yeah.

swyx: See I was very natural.

Ryan Lopopolo: Its success has been part of what I have been building toward and it is, it has grown quite well, right?

Yeah. We have durable products in the lines of business that are built outta there a ton of zero to one work happening as well, which is the core essence of the way we do applied AI work at the company to sprint after it new to figure out where we can actually successfully deploy the model.

Yeah. Yes. A hundred percent. We also have a New York office too that has a ton of engineering presence.

swyx: Yeah. Exact. Exactly. That’s these are my road roadmaps for a e wherever people hiring engineers, I will go. That’s right. Ra it’s

Vibhu: a cool office to New York is a old REI building, I believe the REI office.

swyx: It’s just No, you’ll never be as big. New York is you can’t get [01:12:00] the size of office that they need.

Ryan Lopopolo: The New York office, Seattle user has a very office Mad Men vibe. It’s beautiful. The Bellevue one is very green, gold fixtures, very Pacific Northwest is very cool place to the vibe.

Be local

Vibhu: little, yeah. A lot of people are like there for people like New York. They wanna be in New York, right?

Ryan Lopopolo: Yeah. Yeah. We have a fantastic workplace team that has been building out these offices. It really is a privilege to work here. Yeah. Excellent. Okay. Thank you for your time. You’ve been very

swyx: generous and you’re, you’ve been cooking, so I’m gonna let you get back to cooking.

It’s been amazing to be with you folks. Happy Friday. Happy Friday.
Discussion about this episodeCommentsRestacks
Latent Space: The AI Engineer PodcastThe podcast by and for AI Engineers! In 2025, over 10 million readers and listeners came to Latent Space to hear about news, papers and interviews in Software 3.0.We cover Foundation Models changing every domain in Code Generation, Multimodality, AI Agents, GPU Infra and more, directly from the founders, builders, and thinkers involved in pushing the cutting edge. Striving to give you both the definitive take on the Current Thing down to the first introduction to the tech you'll be using in the next 3 months! We break news and exclusive interviews from OpenAI, Anthropic, Gemini, Meta (Soumith Chintala), Sierra (Bret Taylor), tiny (George Hotz), Databricks/MosaicML (Jon Frankle), Modular (Chris Lattner), Answer.ai (Jeremy Howard), et al. Full show notes always on https://latent.spaceThe podcast by and for AI Engineers! In 2025, over 10 million readers and listeners came to Latent Space to hear about news, papers and interviews in Software 3.0.

We cover Foundation Models changing every domain in Code Generation, Multimodality, AI Agents, GPU Infra and more, directly from the founders, builders, and thinkers involved in pushing the cutting edge. Striving to give you both the definitive take on the Current Thing down to the first introduction to the tech you'll be using in the next 3 months! We break news and exclusive interviews from OpenAI, Anthropic, Gemini, Meta (Soumith Chintala), Sierra (Bret Taylor), tiny (George Hotz), Databricks/MosaicML (Jon Frankle), Modular (Chris Lattner), Answer.ai (Jeremy Howard), et al. 

Full show notes always on https://latent.spaceSubscribeListen onSubstack AppApple PodcastsSpotifyRSS FeedRecent Episodes

Notion’s Token Town: 5 Rebuilds, 100+ Tools, MCP vs CLIs and the Software Factory Future — Simon Last & Sarah Sachs of Notion3 hrs ago

Marc Andreessen introspects on The Death of the Browser, Pi + OpenClaw, and Why "This Time Is Different"Apr 3

Moonlake: Causal World Models should be Multimodal, Interactive, and Efficient — with Chris Manning and Fan-yun SunApr 2

Mistral: Voxtral TTS, Forge, Leanstral, & what's next for Mistral 4 — w/ Pavan Kumar Reddy & Guillaume LampleMar 30

🔬Why There Is No "AlphaFold for Materials" — AI for Materials Discovery with Heather KulikMar 24 • Brandon Anderson and RJ Honicky

Dreamer: the Personal Agent OS — David SingletonMar 20

Why Anthropic Thinks AI Should Have Its Own Computer — Felix Rieseberg of Claude Cowork & Claude Code DesktopMar 17
## Ready for more?
Subscribe© 2026 Latent.Space · Privacy ∙ Terms ∙ Collection notice

 Start your SubstackGet the appSubstack is the home for great culture
 

 
 
 
 

 
 
 
 
 window._preloads = JSON.parse("{\"isEU\":false,\"language\":\"en\",\"country\":\"US\",\"userLocale\":{\"language\":\"en\",\"region\":\"US\",\"source\":\"default\"},\"base_url\":\"https://www.latent.space\",\"stripe_publishable_key\":\"pk_live_51QfnARLDSWi1i85FBpvw6YxfQHljOpWXw8IKi5qFWEzvW8HvoD8cqTulR9UWguYbYweLvA16P7LN6WZsGdZKrNkE00uGbFaOE3\",\"captcha_site_key\":\"6LeI15YsAAAAAPXyDcvuVqipba_jEFQCjz1PFQoz\",\"pub\":{\"apple_pay_disabled\":false,\"apex_domain\":null,\"author_id\":89230629,\"byline_images_enabled\":true,\"bylines_enabled\":true,\"chartable_token\":null,\"community_enabled\":true,\"copyright\":\"Latent.Space\",\"cover_photo_url\":null,\"created_at\":\"2022-09-12T05:38:09.694Z\",\"custom_domain_optional\":false,\"custom_domain\":\"www.latent.space\",\"default_comment_sort\":\"best_first\",\"default_coupon\":null,\"default_group_coupon\":\"26e3a27d\",\"default_show_guest_bios\":true,\"email_banner_url\":null,\"email_from_name\":\"Latent.Space\",\"email_from\":null,\"embed_tracking_disabled\":false,\"explicit\":false,\"expose_paywall_content_to_search_engines\":true,\"fb_pixel_id\":null,\"fb_site_verification_token\":null,\"flagged_as_spam\":false,\"founding_subscription_benefits\":[\"If we've meaningfully impacted your work/thinking!\"],\"free_subscription_benefits\":[\"All podcasts + public/guest posts\"],\"ga_pixel_id\":null,\"google_site_verification_token\":null,\"google_tag_manager_token\":null,\"hero_image\":null,\"hero_text\":\"The AI Engineer newsletter + Top technical AI podcast. How leading labs build Agents, Models, Infra, & AI for Science. See https://latent.space/about for highlights from Greg Brockman, Andrej Karpathy, George Hotz, Simon Willison, Soumith Chintala et al!\",\"hide_intro_subtitle\":null,\"hide_intro_title\":null,\"hide_podcast_feed_link\":false,\"homepage_type\":\"magaziney\",\"id\":1084089,\"image_thumbnails_always_enabled\":false,\"invite_only\":false,\"hide_podcast_from_pub_listings\":false,\"language\":\"en\",\"logo_url_wide\":\"https://substackcdn.com/image/fetch/$s_!1PJi!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa4fe1182-38af-4a5d-bacc-439c36225e87_5000x1200.png\",\"logo_url\":\"https://substackcdn.com/image/fetch/$s_!DbYa!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F73b0838a-bd14-46a1-801c-b6a2046e5c1e_1130x1130.png\",\"minimum_group_size\":2,\"moderation_enabled\":true,\"name\":\"Latent.Space\",\"paid_subscription_benefits\":[\"Support the podcast and newsletter work we do!\",\"Weekday full AINews!\"],\"parsely_pixel_id\":null,\"chartbeat_domain\":null,\"payments_state\":\"enabled\",\"paywall_free_trial_enabled\":true,\"podcast_art_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/534f41b9-5d2b-49b9-9578-4852473c362f_1400x1400.png\",\"paid_podcast_episode_art_url\":null,\"podcast_byline\":\"Latent.Space\",\"podcast_description\":\"The podcast by and for AI Engineers! In 2025, over 10 million readers and listeners came to Latent Space to hear about news, papers and interviews in Software 3.0.\\n\\nWe cover Foundation Models changing every domain in Code Generation, Multimodality, AI Agents, GPU Infra and more, directly from the founders, builders, and thinkers involved in pushing the cutting edge. Striving to give you both the definitive take on the Current Thing down to the first introduction to the tech you'll be using in the next 3 months! We break news and exclusive interviews from OpenAI, Anthropic, Gemini, Meta (Soumith Chintala), Sierra (Bret Taylor), tiny (George Hotz), Databricks/MosaicML (Jon Frankle), Modular (Chris Lattner), Answer.ai (Jeremy Howard), et al. \\n\\nFull show notes always on https://latent.space\",\"podcast_enabled\":true,\"podcast_feed_url\":null,\"podcast_title\":\"Latent Space: The AI Engineer Podcast\",\"post_preview_limit\":200,\"primary_user_id\":89230629,\"require_clickthrough\":false,\"show_pub_podcast_tab\":false,\"show_recs_on_homepage\":true,\"subdomain\":\"swyx\",\"subscriber_invites\":0,\"support_email\":null,\"theme_var_background_pop\":\"#0068EF\",\"theme_var_color_links\":true,\"theme_var_cover_bg_color\":null,\"trial_end_override\":null,\"twitter_pixel_id\":null,\"type\":\"newsletter\",\"post_reaction_faces_enabled\":true,\"is_personal_mode\":false,\"plans\":[{\"id\":\"yearly80usd\",\"object\":\"plan\",\"active\":true,\"aggregate_usage\":null,\"amount\":8000,\"amount_decimal\":\"8000\",\"billing_scheme\":\"per_unit\",\"created\":1693620604,\"currency\":\"usd\",\"interval\":\"year\",\"interval_count\":1,\"livemode\":true,\"metadata\":{\"substack\":\"yes\"},\"meter\":null,\"nickname\":\"$80 a year\",\"product\":\"prod_OYqzb0iIwest4i\",\"tiers\":null,\"tiers_mode\":null,\"transform_usage\":null,\"trial_period_days\":null,\"usage_type\":\"licensed\",\"currency_options\":{\"aud\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":12000,\"unit_amount_decimal\":\"12000\"},\"brl\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":41500,\"unit_amount_decimal\":\"41500\"},\"cad\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":11500,\"unit_amount_decimal\":\"11500\"},\"chf\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":6500,\"unit_amount_decimal\":\"6500\"},\"dkk\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":52000,\"unit_amount_decimal\":\"52000\"},\"eur\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":7000,\"unit_amount_decimal\":\"7000\"},\"gbp\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":6500,\"unit_amount_decimal\":\"6500\"},\"mxn\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":143500,\"unit_amount_decimal\":\"143500\"},\"nok\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":77500,\"unit_amount_decimal\":\"77500\"},\"nzd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":14000,\"unit_amount_decimal\":\"14000\"},\"pln\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":30000,\"unit_amount_decimal\":\"30000\"},\"sek\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":76000,\"unit_amount_decimal\":\"76000\"},\"usd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":8000,\"unit_amount_decimal\":\"8000\"}}},{\"id\":\"monthly8usd\",\"object\":\"plan\",\"active\":true,\"aggregate_usage\":null,\"amount\":800,\"amount_decimal\":\"800\",\"billing_scheme\":\"per_unit\",\"created\":1693620602,\"currency\":\"usd\",\"interval\":\"month\",\"interval_count\":1,\"livemode\":true,\"metadata\":{\"substack\":\"yes\"},\"meter\":null,\"nickname\":\"$8 a month\",\"product\":\"prod_OYqz6hS4QhIgDK\",\"tiers\":null,\"tiers_mode\":null,\"transform_usage\":null,\"trial_period_days\":null,\"usage_type\":\"licensed\",\"currency_options\":{\"aud\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":1200,\"unit_amount_decimal\":\"1200\"},\"brl\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":4200,\"unit_amount_decimal\":\"4200\"},\"cad\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":1200,\"unit_amount_decimal\":\"1200\"},\"chf\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":700,\"unit_amount_decimal\":\"700\"},\"dkk\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":5500,\"unit_amount_decimal\":\"5500\"},\"eur\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":700,\"unit_amount_decimal\":\"700\"},\"gbp\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":700,\"unit_amount_decimal\":\"700\"},\"mxn\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":14500,\"unit_amount_decimal\":\"14500\"},\"nok\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":8000,\"unit_amount_decimal\":\"8000\"},\"nzd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":1400,\"unit_amount_decimal\":\"1400\"},\"pln\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":3000,\"unit_amount_decimal\":\"3000\"},\"sek\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":8000,\"unit_amount_decimal\":\"8000\"},\"usd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":800,\"unit_amount_decimal\":\"800\"}}},{\"id\":\"founding12300usd\",\"name\":\"founding12300usd\",\"nickname\":\"founding12300usd\",\"active\":true,\"amount\":12300,\"currency\":\"usd\",\"interval\":\"year\",\"interval_count\":1,\"metadata\":{\"substack\":\"yes\",\"founding\":\"yes\",\"no_coupons\":\"yes\",\"short_description\":\"Latent Spacenaut\",\"short_description_english\":\"Latent Spacenaut\",\"minimum\":\"12300\",\"minimum_local\":{\"aud\":17500,\"brl\":62000,\"cad\":17000,\"chf\":10000,\"dkk\":78000,\"eur\":10500,\"gbp\":9500,\"mxn\":212500,\"nok\":116500,\"nzd\":21000,\"pln\":44500,\"sek\":113000,\"usd\":12500}},\"currency_options\":{\"aud\":{\"unit_amount\":17500,\"tax_behavior\":\"unspecified\"},\"brl\":{\"unit_amount\":62000,\"tax_behavior\":\"unspecified\"},\"cad\":{\"unit_amount\":17000,\"tax_behavior\":\"unspecified\"},\"chf\":{\"unit_amount\":10000,\"tax_behavior\":\"unspecified\"},\"dkk\":{\"unit_amount\":78000,\"tax_behavior\":\"unspecified\"},\"eur\":{\"unit_amount\":10500,\"tax_behavior\":\"unspecified\"},\"gbp\":{\"unit_amount\":9500,\"tax_behavior\":\"unspecified\"},\"mxn\":{\"unit_amount\":212500,\"tax_behavior\":\"unspecified\"},\"nok\":{\"unit_amount\":116500,\"tax_behavior\":\"unspecified\"},\"nzd\":{\"unit_amount\":21000,\"tax_behavior\":\"unspecified\"},\"pln\":{\"unit_amount\":44500,\"tax_behavior\":\"unspecified\"},\"sek\":{\"unit_amount\":113000,\"tax_behavior\":\"unspecified\"},\"usd\":{\"unit_amount\":12500,\"tax_behavior\":\"unspecified\"}}}],\"stripe_user_id\":\"acct_1B3pNWKWe8hdGUWL\",\"stripe_country\":\"SG\",\"stripe_publishable_key\":\"pk_live_51B3pNWKWe8hdGUWL8wfT91ugrzbIB6qFqnTzHiUzKR5Sjtm52KIOo0M5yhuAokI02qFay5toW4QfOsJttHMoBivF003gbn4zNC\",\"stripe_platform_account\":\"US\",\"automatic_tax_enabled\":false,\"author_name\":\"Latent.Space\",\"author_handle\":\"swyx\",\"author_photo_url\":\"https://substackcdn.com/image/fetch/$s_!drTb!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdb0f8d45-1eb8-4c02-a120-650d377ee52d_640x640.jpeg\",\"author_bio\":\"Writer, curator, latent space explorer. Main blog: https://swyx.io Devrel/Dev community: https://dx.tips/ Twitter: https://twitter.com/swyx\",\"twitter_screen_name\":\"swyx\",\"has_custom_tos\":false,\"has_custom_privacy\":false,\"theme\":{\"background_pop_color\":\"#9333ea\",\"web_bg_color\":\"#ffffff\",\"cover_bg_color\":\"#ffffff\",\"publication_id\":1084089,\"color_links\":null,\"font_preset_heading\":\"slab\",\"font_preset_body\":\"sans\",\"font_family_headings\":null,\"font_family_body\":null,\"font_family_ui\":null,\"font_size_body_desktop\":null,\"print_secondary\":null,\"custom_css_web\":null,\"custom_css_email\":null,\"home_hero\":\"magaziney\",\"home_posts\":\"custom\",\"home_show_top_posts\":true,\"hide_images_from_list\":false,\"home_hero_alignment\":\"left\",\"home_hero_show_podcast_links\":true,\"default_post_header_variant\":null,\"custom_header\":null,\"custom_footer\":null,\"social_media_links\":null,\"font_options\":null,\"section_template\":null,\"custom_subscribe\":null},\"threads_v2_settings\":{\"photo_replies_enabled\":true,\"first_thread_email_sent_at\":null,\"create_thread_minimum_role\":\"paid\",\"activated_at\":\"2025-09-09T23:28:56.695+00:00\",\"reader_thread_notifications_enabled\":false,\"boost_free_subscriber_chat_preview_enabled\":false,\"push_suppression_enabled\":false},\"default_group_coupon_percent_off\":\"49.00\",\"pause_return_date\":null,\"has_posts\":true,\"has_recommendations\":true,\"first_post_date\":\"2022-09-17T20:35:46.224Z\",\"has_podcast\":true,\"has_free_podcast\":true,\"has_subscriber_only_podcast\":true,\"has_community_content\":true,\"rankingDetail\":\"Thousands of paid subscribers\",\"rankingDetailFreeIncluded\":\"Hundreds of thousands of subscribers\",\"rankingDetailOrderOfMagnitude\":1000,\"rankingDetailFreeIncludedOrderOfMagnitude\":100000,\"rankingDetailFreeSubscriberCount\":\"Over 178,000 subscribers\",\"rankingDetailByLanguage\":{\"ar\":{\"rankingDetail\":\"Thousands of paid subscribers\"},\"ca\":{\"rankingDetail\":\"Milers de subscriptors de pagament\"},\"da\":{\"rankingDetail\":\"Tusindvis af betalte abonnenter\"},\"de\":{\"rankingDetail\":\"Tausende von Paid-Abonnenten\"},\"es\":{\"rankingDetail\":\"Miles de suscriptores de pago\"},\"fr\":{\"rankingDetail\":\"Plusieurs milliers d\u2019abonn\u00E9s payants\"},\"ja\":{\"rankingDetail\":\"\u6570\u5343\u4EBA\u306E\u6709\u6599\u767B\u9332\u8005\"},\"nb\":{\"rankingDetail\":\"Tusenvis av betalende abonnenter\"},\"nl\":{\"rankingDetail\":\"Duizenden betalende abonnees\"},\"pl\":{\"rankingDetail\":\"Tysi\u0105ce p\u0142ac\u0105cych subskrybent\u00F3w\"},\"pt\":{\"rankingDetail\":\"Milhares de subscri\u00E7\u00F5es pagas\"},\"pt-br\":{\"rankingDetail\":\"Milhares de assinantes pagas\"},\"en-gb\":{\"rankingDetail\":\"Thousands of paid subscribers\"},\"it\":{\"rankingDetail\":\"Migliaia di abbonati a pagamento\"},\"tr\":{\"rankingDetail\":\"Binlerce \u00FCcretli abone\"},\"sv\":{\"rankingDetail\":\"Tusentals betalande prenumeranter\"},\"en\":{\"rankingDetail\":\"Thousands of paid subscribers\"}},\"freeSubscriberCount\":\"178,000\",\"freeSubscriberCountOrderOfMagnitude\":\"178K+\",\"author_bestseller_tier\":1000,\"author_badge\":{\"type\":\"bestseller\",\"tier\":1000},\"disable_monthly_subscriptions\":false,\"disable_annual_subscriptions\":false,\"hide_post_restacks\":false,\"notes_feed_enabled\":false,\"showIntroModule\":false,\"isPortraitLayout\":false,\"last_chat_post_at\":\"2025-09-16T10:15:58.593Z\",\"primary_profile_name\":\"Latent.Space\",\"primary_profile_photo_url\":\"https://substackcdn.com/image/fetch/$s_!drTb!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdb0f8d45-1eb8-4c02-a120-650d377ee52d_640x640.jpeg\",\"no_follow\":false,\"paywall_chat\":\"free\",\"sections\":[{\"id\":327741,\"created_at\":\"2026-01-23T16:38:15.607Z\",\"updated_at\":\"2026-02-06T00:29:08.963Z\",\"publication_id\":1084089,\"name\":\"AINews: Weekday Roundups\",\"description\":\"Every Weekday - human-curated, AI-summarized news recaps across all of AI Engineering. See https://www.youtube.com/watch?v=IHkyFhU6JEY for how it works\",\"slug\":\"ainews\",\"is_podcast\":false,\"is_live\":true,\"is_default_on\":true,\"sibling_rank\":2,\"port_status\":\"success\",\"logo_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/9a9e98c6-5aeb-461b-b5d0-54d75773e5fa_124x124.png\",\"hide_from_navbar\":false,\"email_from_name\":\"AINews\",\"hide_posts_from_pub_listings\":true,\"email_banner_url\":null,\"cover_photo_url\":null,\"hide_intro_title\":false,\"hide_intro_subtitle\":false,\"ignore_publication_email_settings\":false,\"custom_config\":{},\"podcastSettings\":null,\"spotifyPodcastSettings\":null,\"pageTheme\":{\"id\":85428,\"publication_id\":1084089,\"section_id\":327741,\"page\":null,\"page_hero\":\"default\",\"page_posts\":\"list\",\"show_podcast_links\":true,\"hero_alignment\":\"left\"},\"showLinks\":[],\"podcastPalette\":{\"DarkMuted\":{\"population\":72,\"rgb\":[73,153,137]},\"DarkVibrant\":{\"population\":6013,\"rgb\":[4,100,84]},\"LightMuted\":{\"population\":7,\"rgb\":[142,198,186]},\"LightVibrant\":{\"population\":3,\"rgb\":[166,214,206]},\"Muted\":{\"population\":6,\"rgb\":[92,164,156]},\"Vibrant\":{\"population\":5,\"rgb\":[76,164,146]}},\"spotify_podcast_settings\":null},{\"id\":335089,\"created_at\":\"2026-02-06T00:32:12.973Z\",\"updated_at\":\"2026-02-10T09:26:47.072Z\",\"publication_id\":1084089,\"name\":\"Latent Space: AI for Science\",\"description\":\"a dedicated channel for Latent Space's AI for Science essays that do not get sent to the broader engineering audience \u2014 opt in if high interest in AI for Science!\",\"slug\":\"cience\",\"is_podcast\":false,\"is_live\":true,\"is_default_on\":true,\"sibling_rank\":3,\"port_status\":\"success\",\"logo_url\":null,\"hide_from_navbar\":false,\"email_from_name\":\"Latent Space Science\",\"hide_posts_from_pub_listings\":false,\"email_banner_url\":null,\"cover_photo_url\":null,\"hide_intro_title\":false,\"hide_intro_subtitle\":false,\"ignore_publication_email_settings\":false,\"custom_config\":{},\"podcastSettings\":null,\"spotifyPodcastSettings\":null,\"pageTheme\":null,\"showLinks\":[],\"podcastPalette\":{\"DarkMuted\":{\"population\":72,\"rgb\":[73,153,137]},\"DarkVibrant\":{\"population\":6013,\"rgb\":[4,100,84]},\"LightMuted\":{\"population\":7,\"rgb\":[142,198,186]},\"LightVibrant\":{\"population\":3,\"rgb\":[166,214,206]},\"Muted\":{\"population\":6,\"rgb\":[92,164,156]},\"Vibrant\":{\"population\":5,\"rgb\":[76,164,146]}},\"spotify_podcast_settings\":null}],\"didIdentity\":\"did:plc:es3srknleppmlecmx45g2hoe\",\"multipub_migration\":null,\"navigationBarItems\":[{\"id\":\"ccf2f42a-8937-4639-b19f-c9f4de0e156c\",\"publication_id\":1084089,\"sibling_rank\":0,\"link_title\":null,\"link_url\":null,\"section_id\":null,\"post_id\":null,\"is_hidden\":true,\"standard_key\":\"archive\",\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"b729d56f-08c1-4100-ab1a-205d81648d74\",\"publication_id\":1084089,\"sibling_rank\":1,\"link_title\":null,\"link_url\":null,\"section_id\":null,\"post_id\":null,\"is_hidden\":true,\"standard_key\":\"leaderboard\",\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"8beddb9c-dd08-4f26-8ee0-b070c1512234\",\"publication_id\":1084089,\"sibling_rank\":2,\"link_title\":\"YouTube\",\"link_url\":\"https://www.youtube.com/playlist?list=PLWEAb1SXhjlfkEF_PxzYHonU_v5LPMI8L\",\"section_id\":null,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"32147b98-9d0e-4489-9749-a205af5d5880\",\"publication_id\":1084089,\"sibling_rank\":3,\"link_title\":\"X\",\"link_url\":\"https://x.com/latentspacepod\",\"section_id\":null,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"eb9e689e-85ee-41b2-af34-dd39a2056c7b\",\"publication_id\":1084089,\"sibling_rank\":4,\"link_title\":\"Discord & Meetups\",\"link_url\":\"\",\"section_id\":null,\"post_id\":115665083,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":{\"id\":115665083,\"slug\":\"community\",\"title\":\"Join the Latent.Space Community!\",\"type\":\"page\"},\"section\":null,\"children\":[]},{\"id\":\"338b842e-22f3-4c36-aa92-1c7ebea574d2\",\"publication_id\":1084089,\"sibling_rank\":7,\"link_title\":\"Write for us!\",\"link_url\":\"https://docs.google.com/forms/d/e/1FAIpQLSeHQAgupNkVRgjNfMJG9d7SFTWUytdS6SNCJVkd0SMNMXHHwA/viewform\",\"section_id\":null,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"fc1a55a0-4a35-46e2-8f57-23b3b668d2cc\",\"publication_id\":1084089,\"sibling_rank\":9999,\"link_title\":null,\"link_url\":null,\"section_id\":335089,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":{\"id\":335089,\"slug\":\"cience\",\"name\":\"Latent Space: AI for Science\",\"hide_from_navbar\":false,\"is_podcast\":false,\"logo_url\":null},\"children\":[]},{\"id\":\"d1605792-17ef-44bf-b2a9-42bf42907f5f\",\"publication_id\":1084089,\"sibling_rank\":9999,\"link_title\":null,\"link_url\":null,\"section_id\":327741,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":{\"id\":327741,\"slug\":\"ainews\",\"name\":\"AINews: Weekday Roundups\",\"hide_from_navbar\":false,\"is_podcast\":false,\"logo_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/9a9e98c6-5aeb-461b-b5d0-54d75773e5fa_124x124.png\"},\"children\":[]}],\"contributors\":[{\"name\":\"Latent.Space\",\"handle\":\"swyx\",\"role\":\"admin\",\"owner\":true,\"user_id\":89230629,\"photo_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/db0f8d45-1eb8-4c02-a120-650d377ee52d_640x640.jpeg\",\"bio\":\"Writer, curator, latent space explorer. Main blog: https://swyx.io Devrel/Dev community: https://dx.tips/ Twitter: https://twitter.com/swyx\"}],\"threads_v2_enabled\":false,\"viralGiftsConfig\":{\"id\":\"70ab6904-f65b-4d85-9447-df0494958717\",\"publication_id\":1084089,\"enabled\":false,\"gifts_per_user\":5,\"gift_length_months\":1,\"send_extra_gifts\":true,\"message\":\"The AI Engineer newsletter + Top 10 US Tech podcast. Exploring AI UX, Agents, Devtools, Infra, Open Source Models. See https://latent.space/about for highlights from Chris Lattner, Andrej Karpathy, George Hotz, Simon Willison, Emad Mostaque, et al!\",\"created_at\":\"2024-12-19T21:55:43.55283+00:00\",\"updated_at\":\"2024-12-19T21:55:43.55283+00:00\",\"days_til_invite\":14,\"send_emails\":true,\"show_link\":null},\"tier\":2,\"no_index\":false,\"can_set_google_site_verification\":true,\"can_have_sitemap\":true,\"founding_plan_name_english\":\"Latent Spacenaut\",\"bundles\":[],\"base_url\":\"https://www.latent.space\",\"hostname\":\"www.latent.space\",\"is_on_substack\":false,\"show_links\":[{\"id\":35417,\"publication_id\":1084089,\"section_id\":null,\"url\":\"https://podcasts.apple.com/us/podcast/latent-space-the-ai-engineer-podcast/id1674008350\",\"platform\":\"apple_podcasts\"},{\"id\":27113,\"publication_id\":1084089,\"section_id\":null,\"url\":\"https://open.spotify.com/show/7wd4eyLPJvtWnUK1ugH1oi\",\"platform\":\"spotify\"},{\"id\":27114,\"publication_id\":1084089,\"section_id\":null,\"url\":\"https://open.spotify.com/show/7wd4eyLPJvtWnUK1ugH1oi\",\"platform\":\"spotify_for_paid_users\"}],\"spotify_podcast_settings\":{\"id\":7020,\"publication_id\":1084089,\"section_id\":null,\"spotify_access_token\":\"7b7a1a8a-d456-4883-8107-3b04d028beab\",\"spotify_uri\":\"spotify:show:7wd4eyLPJvtWnUK1ugH1oi\",\"spotify_podcast_title\":null,\"created_at\":\"2024-04-17T14:40:50.766Z\",\"updated_at\":\"2024-04-17T14:42:36.242Z\",\"currently_published_on_spotify\":true,\"feed_url_for_spotify\":\"https://api.substack.com/feed/podcast/spotify/7b7a1a8a-d456-4883-8107-3b04d028beab/1084089.rss\",\"spotify_show_url\":\"https://open.spotify.com/show/7wd4eyLPJvtWnUK1ugH1oi\"},\"podcastPalette\":{\"Vibrant\":{\"rgb\":[204,105,26],\"population\":275},\"DarkVibrant\":{\"rgb\":[127,25,90],\"population\":313},\"LightVibrant\":{\"rgb\":[212,111,247],\"population\":333},\"Muted\":{\"rgb\":[152,69,68],\"population\":53},\"DarkMuted\":{\"rgb\":[50,23,49],\"population\":28},\"LightMuted\":{\"rgb\":[109.71710526315789,8.052631578947365,144.94736842105263],\"population\":0}},\"pageThemes\":{\"podcast\":null},\"multiple_pins\":true,\"live_subscriber_counts\":false,\"supports_ip_content_unlock\":false,\"appTheme\":{\"colors\":{\"accent\":{\"name\":\"#9333ea\",\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":126,\"g\":28,\"b\":214,\"a\":1},\"primary_elevated\":{\"r\":126,\"g\":28,\"b\":214,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"bg_hover\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.3},\"dark\":{\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"primary_elevated\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"bg_hover\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.3}}},\"fg\":{\"primary\":{\"r\":0,\"g\":0,\"b\":0,\"a\":0.8},\"secondary\":{\"r\":0,\"g\":0,\"b\":0,\"a\":0.6},\"tertiary\":{\"r\":0,\"g\":0,\"b\":0,\"a\":0.4},\"accent\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"dark\":{\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.9},\"secondary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.6},\"tertiary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.4},\"accent\":{\"r\":174,\"g\":77,\"b\":255,\"a\":1}}},\"bg\":{\"name\":\"#ffffff\",\"hue\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0},\"tint\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0},\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"primary_hover\":{\"r\":250,\"g\":250,\"b\":250,\"a\":1},\"primary_elevated\":{\"r\":250,\"g\":250,\"b\":250,\"a\":1},\"secondary\":{\"r\":238,\"g\":238,\"b\":238,\"a\":1},\"secondary_elevated\":{\"r\":206.90096477355226,\"g\":206.90096477355175,\"b\":206.9009647735519,\"a\":1},\"tertiary\":{\"r\":219,\"g\":219,\"b\":219,\"a\":1},\"quaternary\":{\"r\":182,\"g\":182,\"b\":182,\"a\":1},\"dark\":{\"primary\":{\"r\":22,\"g\":23,\"b\":24,\"a\":1},\"primary_hover\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"primary_elevated\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"secondary\":{\"r\":35,\"g\":37,\"b\":37,\"a\":1},\"secondary_elevated\":{\"r\":41.35899397549579,\"g\":43.405356429195315,\"b\":43.40489285041963,\"a\":1},\"tertiary\":{\"r\":54,\"g\":55,\"b\":55,\"a\":1},\"quaternary\":{\"r\":90,\"g\":91,\"b\":91,\"a\":1}}}},\"cover_image\":{\"url\":\"https://substackcdn.com/image/fetch/$s_!1PJi!,w_1200,h_400,c_pad,f_auto,q_auto:best,fl_progressive:steep,b_auto:border,b_rgb:ffffff/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa4fe1182-38af-4a5d-bacc-439c36225e87_5000x1200.png\",\"height\":400,\"width\":5000}},\"portalAppTheme\":{\"colors\":{\"accent\":{\"name\":\"#9333ea\",\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":135,\"g\":28,\"b\":232,\"a\":1},\"primary_elevated\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":255,\"g\":103,\"b\":25,\"a\":0.2},\"bg_hover\":{\"r\":255,\"g\":103,\"b\":25,\"a\":0.3},\"dark\":{\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"primary_elevated\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"bg_hover\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.3}}},\"fg\":{\"primary\":{\"r\":54,\"g\":55,\"b\":55,\"a\":1},\"secondary\":{\"r\":134,\"g\":135,\"b\":135,\"a\":1},\"tertiary\":{\"r\":146,\"g\":146,\"b\":146,\"a\":1},\"accent\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"dark\":{\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.9},\"secondary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.6},\"tertiary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.4},\"accent\":{\"r\":174,\"g\":77,\"b\":255,\"a\":1}}},\"bg\":{\"name\":\"#ffffff\",\"hue\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"tint\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"primary_hover\":{\"r\":240,\"g\":240,\"b\":240,\"a\":1},\"primary_elevated\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"secondary\":{\"r\":240,\"g\":240,\"b\":240,\"a\":1},\"secondary_elevated\":{\"r\":240,\"g\":240,\"b\":240,\"a\":1},\"tertiary\":{\"r\":221,\"g\":221,\"b\":221,\"a\":1},\"quaternary\":{\"r\":183,\"g\":183,\"b\":183,\"a\":1},\"dark\":{\"primary\":{\"r\":22,\"g\":23,\"b\":24,\"a\":1},\"primary_hover\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"primary_elevated\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"secondary\":{\"r\":35,\"g\":37,\"b\":37,\"a\":1},\"secondary_elevated\":{\"r\":41.35899397549579,\"g\":43.405356429195315,\"b\":43.40489285041963,\"a\":1},\"tertiary\":{\"r\":54,\"g\":55,\"b\":55,\"a\":1},\"quaternary\":{\"r\":90,\"g\":91,\"b\":91,\"a\":1}}},\"wordmark_bg\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1}},\"fonts\":{\"heading\":\"slab\",\"body\":\"sans\"}},\"logoPalette\":{\"Vibrant\":{\"rgb\":[200,99,28],\"population\":378},\"DarkVibrant\":{\"rgb\":[12,77,99],\"population\":37},\"LightVibrant\":{\"rgb\":[212,110,247],\"population\":348},\"Muted\":{\"rgb\":[152,68,67],\"population\":50},\"DarkMuted\":{\"rgb\":[122,64,142],\"population\":19},\"LightMuted\":{\"rgb\":[109.99999999999996,8,145],\"population\":0}}},\"confirmedLogin\":false,\"hide_intro_popup\":false,\"block_auto_login\":false,\"domainInfo\":{\"isSubstack\":false,\"customDomain\":\"www.latent.space\"},\"experimentFeatures\":{},\"experimentExposures\":{},\"siteConfigs\":{\"score_upsell_email\":\"control\",\"first_chat_email_enabled\":true,\"reader-onboarding-promoted-pub\":737237,\"new_commenter_approval\":false,\"pub_update_opennode_api_key\":false,\"notes_video_max_duration_minutes\":15,\"show_content_label_age_gating_in_feed\":false,\"zendesk_automation_cancellations\":false,\"hide_book_a_meeting_button\":false,\"enable_saved_segments\":false,\"mfa_action_box_enabled\":false,\"publication_max_bylines\":35,\"no_contest_charge_disputes\":false,\"feed_posts_previously_seen_weight\":0.1,\"publication_tabs_reorder\":false,\"comp_expiry_email_new_copy\":\"NONE\",\"free_unlock_required\":false,\"traffic_rule_check_enabled\":false,\"amp_emails_enabled\":false,\"enable_post_summarization\":false,\"live_stream_host_warning_message\":\"\",\"bitcoin_enabled\":false,\"minimum_ios_os_version\":\"17.0.0\",\"show_entire_square_image\":false,\"hide_subscriber_count\":false,\"fit_in_live_stream_player\":false,\"publication_author_display_override\":\"\",\"ios_webview_payments_enabled\":\"control\",\"generate_pdf_tax_report\":false,\"hide_post_sidebar\":false,\"show_generic_post_importer\":false,\"enable_pledges_modal\":true,\"include_pdf_invoice\":false,\"notes_weight_watch_video\":5,\"enable_react_dashboard\":false,\"meetings_v1\":false,\"enable_videos_page\":false,\"exempt_from_gtm_filter\":false,\"group_sections_and_podcasts_in_menu\":false,\"boost_optin_modal_enabled\":true,\"standards_and_enforcement_features_enabled\":false,\"pub_creation_captcha_behavior\":\"risky_pubs_or_rate_limit\",\"post_blogspot_importer\":false,\"notes_weight_short_item_boost\":0.15,\"enable_high_res_background_uploading\":false,\"pub_tts_override\":\"default\",\"disable_monthly_subscriptions\":false,\"skip_welcome_email\":false,\"chat_reader_thread_notification_default\":false,\"scheduled_pinned_posts\":false,\"disable_redirect_outbound_utm_params\":false,\"reader_gift_referrals_enabled\":true,\"dont_show_guest_byline\":false,\"like_comments_enabled\":true,\"temporal_livestream_ended_draft\":true,\"enable_author_note_email_toggle\":false,\"meetings_embed_publication_name\":false,\"fallback_to_archive_search_on_section_pages\":false,\"livekit_track_egress_custom_base_url\":\"http://livekit-egress-custom-recorder-participant-test.s3-website-us-east-1.amazonaws.com\",\"welcome_screen_blurb_override\":\"\",\"notes_weight_low_impression_boost\":0.3,\"like_posts_enabled\":true,\"feed_promoted_video_boost\":1.5,\"twitter_player_card_enabled\":true,\"subscribe_bypass_preact_router\":false,\"feed_promoted_user\":false,\"show_note_stats_for_all_notes\":false,\"section_specific_csv_imports_enabled\":false,\"disable_podcast_feed_description_cta\":false,\"bypass_profile_substack_logo_detection\":false,\"use_preloaded_player_sources\":false,\"enable_tiktok_oauth\":false,\"list_pruning_enabled\":false,\"facebook_connect\":false,\"opt_in_to_sections_during_subscribe\":false,\"dpn_weight_share\":2,\"underlined_colored_links\":false,\"enable_efficient_digest_embed\":false,\"extract_stripe_receipt_url\":false,\"enable_aligned_images\":false,\"max_image_upload_mb\":64,\"threads_suggested_ios_version\":null,\"pledges_disabled\":false,\"threads_minimum_ios_version\":812,\"hide_podcast_email_setup_link\":false,\"subscribe_captcha_behavior\":\"default\",\"publication_ban_sample_rate\":0,\"enable_note_polls\":false,\"ios_enable_publication_activity_tab\":false,\"custom_themes_substack_subscribe_modal\":false,\"ios_post_share_assets_screenshot_trigger\":\"control\",\"opt_in_to_sections_during_subscribe_include_main_pub_newsletter\":false,\"continue_support_cta_in_newsletter_emails\":false,\"bloomberg_syndication_enabled\":false,\"welcome_page_app_button\":true,\"lists_enabled\":false,\"adhoc_email_batch_delay_ms\":0,\"generated_database_maintenance_mode\":false,\"allow_document_freeze\":false,\"test_age_gate_user\":false,\"podcast_main_feed_is_firehose\":false,\"pub_app_incentive_gift\":\"\",\"no_embed_redirect\":false,\"customized_email_from_name_for_new_follow_emails\":\"treatment\",\"spotify_open_access_sandbox_mode\":false,\"disable_custom_nav_menu\":false,\"fullstory_enabled\":false,\"chat_reply_poll_interval\":3,\"dpn_weight_follow_or_subscribe\":3,\"thefp_enable_email_upsell_banner\":false,\"force_pub_links_to_use_subdomain\":false,\"always_show_cookie_banner\":false,\"hide_media_download_option\":false,\"hide_post_restacks\":false,\"feed_item_source_debug_mode\":false,\"ios_subscription_bar_live_polling_enabled\":true,\"enable_user_status_ui\":false,\"publication_homepage_title_display_override\":\"\",\"live_stream_founding_audience_enabled\":true,\"post_preview_highlight_byline\":false,\"4k_video\":false,\"enable_islands_section_intent_screen\":false,\"post_metering_enabled\":false,\"notifications_disabled\":\"\",\"cross_post_notification_threshold\":1000,\"facebook_connect_prod_app\":true,\"force_into_pymk_ranking\":false,\"minimum_android_version\":756,\"live_stream_krisp_noise_suppression_enabled\":false,\"enable_transcription_translations\":false,\"use_og_image_as_twitter_image_for_post_previews\":false,\"always_use_podcast_channel_art_as_episode_art_in_rss\":false,\"enable_sponsorship_perks\":false,\"seo_tier_override\":\"NONE\",\"editor_role_enabled\":false,\"no_follow_links\":false,\"publisher_api_enabled\":false,\"zendesk_support_priority\":\"default\",\"enable_post_clips_stats\":false,\"enable_subscriber_referrals_awards\":true,\"ios_profile_themes_feed_permalink_enabled\":false,\"include_thumbnail_landscape_layouts\":true,\"use_publication_language_for_transcription\":false,\"show_substack_funded_gifts_tooltip\":true,\"disable_ai_transcription\":false,\"thread_permalink_preview_min_ios_version\":4192,\"android_toggle_on_website_enabled\":false,\"internal_android_enable_post_editor\":false,\"enable_pencraft_sandbox_access\":false,\"updated_inbox_ui\":false,\"nav_group_items\":true,\"live_stream_creation_enabled\":true,\"disable_card_element_in_europe\":false,\"web_growth_item_promotion_threshold\":0,\"bundle_subscribe_enabled\":false,\"enable_web_typing_indicators\":false,\"web_vitals_sample_rate\":0,\"allow_live_stream_auto_takedown\":\"true\",\"mobile_publication_attachments_enabled\":false,\"ios_post_dynamic_title_size\":false,\"ios_enable_live_stream_highlight_trailer_toggle\":false,\"ai_image_generation_enabled\":true,\"disable_personal_substack_initialization\":false,\"section_specific_welcome_pages\":false,\"local_payment_methods\":\"control\",\"publisher_api_cancel_comp\":false,\"posts_in_rss_feed\":20,\"post_rec_endpoint\":\"\",\"publisher_dashboard_section_selector\":false,\"reader_surveys_platform_question_order\":\"36,1,4,2,3,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35\",\"developer_api_enabled\":false,\"login_guard_app_link_in_email\":true,\"community_moderators_enabled\":false,\"enable_custom_theme\":false,\"monthly_sub_is_one_off\":false,\"unread_notes_activity_digest\":\"control\",\"display_cookie_settings\":false,\"welcome_page_query_params\":false,\"enable_free_podcast_urls\":false,\"email_post_stats_v2\":false,\"comp_expiry_emails_disabled\":false,\"enable_description_on_polls\":false,\"use_microlink_for_instagram_embeds\":false,\"post_notification_batch_delay_ms\":30000,\"free_signup_confirmation_behavior\":\"with_email_validation\",\"android_reset_backstack_after_timeout\":true,\"ios_post_stats_for_admins\":false,\"enable_livestream_branding\":true,\"use_livestream_post_media_composition\":true,\"section_specific_preambles\":false,\"pub_export_temp_disable\":false,\"show_menu_on_posts\":false,\"ios_post_subscribe_web_routing\":true,\"ios_writer_stats_public_launch_v2\":false,\"include_thumbnail_book_cover_layouts\":false,\"enable_android_post_stats\":false,\"ios_chat_revamp_enabled\":false,\"app_onboarding_survey_email\":false,\"republishing_enabled\":false,\"app_mode\":false,\"show_phone_banner\":true,\"live_stream_video_enhancer\":\"internal\",\"minimum_ios_version\":2200,\"enable_author_pages\":false,\"enable_decagon_chat\":true,\"first_month_upsell\":\"control\",\"enable_subscriber_tags\":false,\"new_user_checklist_enabled\":\"use_follower_count\",\"ios_feed_note_status_polling_enabled\":false,\"latex_upgraded_inline\":false,\"show_attached_profile_for_pub_setting\":false,\"rss_verification_code\":\"\",\"notification_post_emails\":\"experiment\",\"notes_weight_follow\":3.8,\"chat_suppress_contributor_push_option_enabled\":false,\"caption_presets_enabled\":false,\"export_hooks_enabled\":false,\"audio_encoding_bitrate\":null,\"bestseller_pub_override\":false,\"extra_seats_coupon_type\":false,\"post_subdomain_universal_links\":false,\"post_import_max_file_size\":26214400,\"feed_promoted_video_publication\":false,\"livekit_reconnect_slate_url\":\"https://mux-livestream-assets.s3.us-east-1.amazonaws.com/custom-disconnect-slate-tall.png\",\"exclude_from_pymk_suggestions\":false,\"publication_ranking_variant\":\"experiment\",\"disable_annual_subscriptions\":false,\"hack_jane_manchun_wong\":true,\"android_enable_auto_gain_control\":true,\"enable_android_dms\":false,\"allow_coupons_on_upgrade\":false,\"test_au_age_gate_user\":false,\"pub_auto_moderation_enabled\":false,\"disable_live_stream_ai_trimming_by_default\":false,\"disable_deletion\":false,\"ios_default_coupon_enabled\":false,\"notes_weight_read_post\":5,\"notes_weight_reply\":3,\"livekit_egress_custom_base_url\":\"http://livekit-egress-custom-recorder.s3-website-us-east-1.amazonaws.com\",\"clip_focused_video_upload_flow\":false,\"live_stream_max_guest_users\":2,\"android_upgrade_alert_dialog_reincarnated\":true,\"enable_video_seo_data\":false,\"can_reimport_unsubscribed_users_with_2x_optin\":false,\"feed_posts_weight_subscribed\":0,\"founding_upgrade_during_gift_disabled\":false,\"ios_feed_subscribe_upsell\":\"treatment_chill_inline\",\"review_incoming_email\":\"default\",\"media_feed_subscribed_posts_weight\":0.5,\"enable_founding_gifts\":false,\"enable_creator_agency_pages\":false,\"enable_sponsorship_campaigns\":false,\"thread_permalink_preview_min_android_version\":2037,\"enable_creator_earnings\":true,\"thefp_enable_embed_media_links\":false,\"thumbnail_selection_max_frames\":300,\"sort_modal_search_results\":false,\"default_thumbnail_time\":10,\"pub_ranking_weight_retained_engagement\":1,\"load_test_unichat\":false,\"notes_read_post_baseline\":0,\"live_stream_head_alignment_guide\":false,\"show_open_post_as_pdf_button\":false,\"free_press_combo_subscribe_flow_enabled\":false,\"android_note_auto_share_assets\":\"control\",\"pub_ranking_weight_immediate_engagement\":0.5,\"enable_portal_feed_post_comments\":false,\"gifts_from_substack_feature_available\":true,\"disable_ai_clips\":false,\"enable_elevenlabs_voiceovers\":false,\"thefp_enable_transcripts\":false,\"use_web_livestream_thumbnail_editor\":true,\"show_simple_post_editor\":false,\"instacart_integration_enabled\":false,\"enable_publication_podcasts_page\":false,\"android_profile_share_assets_experiment\":\"treatment\",\"use_advanced_fonts\":false,\"ios_note_composer_settings_enabled\":false,\"android_v2_post_video_player_enabled\":false,\"enable_direct_message_request_bypass\":false,\"enable_apple_news_sync\":false,\"live_stream_in_trending_topic_overrides\":\"\",\"media_feed_prepend_inbox_limit\":30,\"free_press_newsletter_promo_enabled\":false,\"enable_ios_livestream_stats\":true,\"disable_live_stream_reactions\":false,\"feed_posts_weight_negative\":2.5,\"instacart_partner_id\":\"\",\"clip_generation_3rd_party_vendor\":\"internal\",\"welcome_page_no_opt_out\":false,\"android_onboarding_swipeable_cards_v2\":\"control\",\"notes_weight_negative\":1,\"ios_discover_tab_min_installed_date\":\"2025-06-09T16:56:58+0000\",\"notes_weight_click_see_more\":2,\"edit_profile_theme_colors\":false,\"notes_weight_like\":2.4,\"disable_clipping_for_readers\":false,\"feed_posts_weight_share\":6,\"android_creator_earnings_enabled\":true,\"feed_posts_weight_reply\":3,\"feed_posts_weight_like\":1.5,\"ios_listen_tab_v2\":\"control\",\"feed_posts_weight_save\":3,\"enable_press_kit_preview_modal\":false,\"dpn_weight_tap_clickbait_penalty\":0.5,\"feed_posts_weight_sign_up\":4,\"live_stream_video_degradation_preference\":\"maintainFramerate\",\"enable_high_follower_dm\":true,\"pause_app_badges\":false,\"android_enable_publication_activity_tab\":false,\"ios_hide_author_in_share_sheet\":\"control\",\"profile_feed_expanded_inventory\":false,\"phone_verification_fallback_to_twilio\":false,\"livekit_mux_latency_mode\":\"low\",\"feed_juiced_user\":0,\"notes_click_see_more_baseline\":0.35,\"enable_polymarket_expandable_embeds\":true,\"publication_onboarding_weight_std_dev\":0,\"can_see_fast_subscriber_counts\":true,\"android_enable_user_status_ui\":false,\"use_advanced_commerce_api_for_iap\":false,\"skip_free_preview_language_in_podcast_notes\":false,\"larger_wordmark_on_publication_homepage\":false,\"video_editor_full_screen\":false,\"enable_mobile_stats_for_admins\":false,\"ios_profile_themes_note_composer_enabled\":false,\"enable_persona_sandbox_environment\":false,\"enable_pinned_portals\":true,\"notes_weight_click_item\":3,\"notes_weight_long_visit\":1,\"create_nav_item_from_tag\":false,\"bypass_single_unlock_token_limit\":false,\"notes_watch_video_baseline\":0.08,\"enable_free_trial_subscription_ios\":true,\"polymarket_minimum_confidence_for_trending_topics\":100,\"add_section_and_tag_metadata\":false,\"daily_promoted_notes_enabled\":true,\"enable_islands_cms\":false,\"enable_livestream_combined_stats\":false,\"ios_social_subgroups_enabled\":false,\"chartbeat_video_enabled\":false,\"enable_drip_campaigns\":false,\"adhoc_email_batch_size\":5000,\"ios_offline_mode_enabled\":false,\"post_management_search_engine\":\"elasticsearch\",\"new_bestseller_leaderboard_feed_item_enabled\":false,\"feed_main_disabled\":false,\"enable_account_settings_revamp\":false,\"allowed_email_domains\":\"one\",\"thefp_enable_fp_recirc_block\":false,\"top_search_variant\":\"control\",\"enable_debug_logs_ios\":false,\"show_pub_content_on_profile_for_pub_id\":0,\"show_pub_content_on_profile\":false,\"livekit_track_egress\":true,\"video_tab_mixture_pattern\":\"npnnnn\",\"enable_theme_contexts\":false,\"onboarding_suggestions_search\":\"experiment\",\"feed_tuner_enabled\":false,\"livekit_mux_latency_mode_rtmp\":\"low\",\"draft_notes_enabled\":true,\"fcm_high_priority\":false,\"enable_drop_caps\":true,\"highlighted_code_block_enabled\":true,\"dpn_weight_tap_bonus_subscribed\":0,\"iap_announcement_blog_url\":\"\",\"android_onboarding_progress_persistence\":\"control\",\"ios_livestream_feedback\":false,\"founding_plan_upgrade_warning\":false,\"dpn_weight_like\":3,\"dpn_weight_short_session\":1,\"ios_enable_custom_thumbnail_generation\":true,\"ios_mediaplayer_reply_bar_v2\":false,\"android_view_post_share_assets_employees_only\":false,\"stripe_link_in_payment_element_v3\":\"treatment\",\"enable_notification_email_batching\":true,\"notes_weight_follow_boost\":10,\"profile_portal_theme\":false,\"live_stream_replay\":false,\"ios_hide_portal_tab_bar\":false,\"follow_upsell_rollout_percentage\":30,\"android_activity_item_sharing_experiment\":\"control\",\"live_stream_invite_ttl_seconds\":900000,\"include_founding_plans_coupon_option\":false,\"thefp_enable_cancellation_discount_offer\":false,\"dpn_weight_reply\":2,\"thefp_free_trial_experiment\":\"treatment\",\"android_enable_edit_profile_theme\":false,\"twitter_api_enabled\":true,\"dpn_weight_follow\":3,\"thumbnail_selection_engine\":\"openai\",\"enable_adhoc_email_batching\":0,\"notes_weight_author_low_impression_boost\":0.2,\"disable_audio_enhancement\":false,\"pub_search_variant\":\"control\",\"ignore_video_in_notes_length_limit\":false,\"web_show_scores_on_sports_tab\":false,\"notes_weight_click_share\":3,\"allow_long_videos\":true,\"feed_posts_weight_long_click\":15,\"dpn_score_threshold\":0,\"thefp_annual_subscription_promotion\":\"treatment\",\"dpn_weight_follow_bonus\":0.5,\"enable_fullscreen_post_live_end_screen\":false,\"use_intro_clip_and_branded_intro_by_default\":false,\"use_enhanced_video_embed_player\":true,\"android_reader_share_assets_3\":\"control\",\"email_change_minimum_bot_score\":0,\"mobile_age_verification_learn_more_link\":\"https://on.substack.com/p/our-position-on-the-online-safety\",\"enable_viewing_all_livestream_viewers\":false,\"web_suggested_search_route_recent_search\":\"control\",\"enable_clip_prompt_variant_filtering\":true,\"chartbeat_enabled\":false,\"dpn_weight_disable\":10,\"dpn_ranking_enabled\":true,\"enable_custom_email_css\":false,\"dpn_model_variant\":\"experiment\",\"platform_search_variant\":\"control\",\"enable_apple_podcast_auto_publish\":false,\"linkedin_profile_search_enabled\":false,\"ios_better_top_search_prompt_in_global_search\":\"control\",\"retire_i18n_marketing_pages\":true,\"publication_has_own_app\":false,\"suggested_minimum_ios_version\":0,\"dpn_weight_open\":2.5,\"ios_pogs_stories\":\"experiment\",\"enable_notes_admins\":false,\"trending_topics_module_long_term_experiment\":\"control\",\"enable_suggested_searches\":true,\"enable_subscription_notification_email_batching\":true,\"android_synchronous_push_notif_handling\":\"control\",\"thumbnail_selection_skip_desktop_streams\":false,\"a24_redemption_link\":\"\",\"dpn_weight_tap\":2.5,\"ios_live_stream_auto_gain_enabled\":true,\"dpn_weight_restack\":2,\"dpn_weight_negative\":40,\"enable_publication_tts_player\":false,\"search_retrieval_variant\":\"treatment\",\"session_version_invalidation_enabled\":false,\"thefp_show_pub_app_callout_on_post\":false,\"galleried_feed_attachments\":true,\"web_post_attachment_fallback\":\"treatment\",\"enable_live_stream_thumbnail_treatment_validation\":true,\"forced_featured_topic_id\":\"\",\"ios_audio_captions_disabled\":false,\"related_posts_enabled\":false,\"use_progressive_editor_rollout\":true,\"ios_live_stream_pip_dismiss_v4\":\"control\",\"reply_rate_limit_max_distinct_users_daily\":110,\"galleried_feed_attachments_in_composer\":false,\"android_rank_share_destinations_experiment\":\"control\",\"publisher_banner\":\"\",\"suggested_search_metadata_web_ui\":true,\"mobile_user_attachments_enabled\":false,\"ios_founding_upgrade_button_in_portals_v2\":\"control\",\"feed_weight_language_mismatch_penalty\":0.6,\"default_orange_quote_experiment\":\"control\",\"enable_high_res_recording_workflow\":false,\"people_you_may_know_algorithm\":\"experiment\",\"enable_sponsorship_profile\":false,\"ios_onboarding_multiple_notification_asks\":\"control\",\"ios_founding_upgrade_button_in_portals\":\"control\",\"ios_inline_upgrade_on_feed_items\":\"control\",\"reply_rate_limit_max_distinct_users_monthly\":600,\"show_branded_intro_setting\":false,\"desktop_live_stream_screen_share_audio_enabled\":false,\"search_posts_use_top_search\":false,\"ios_inbox_observe_by_key\":true,\"enable_high_res_background_uploading_session_recovery\":false,\"portal_post_style\":\"control\",\"dpn_weight_long_session\":2,\"use_custom_header_by_default\":false,\"ios_listen_tab\":false,\"android_composer_modes_vs_attachments\":\"control\",\"activity_item_ranking_variant\":\"experiment\",\"android_polymarket_embed_search\":false,\"ios_onboarding_new_user_survey\":\"experiment\",\"android_post_like_share_nudge\":\"treatment\",\"android_post_bottom_share_experiment\":\"treatment\",\"search_ranker_variant\":\"control\",\"use_thumbnail_selection_sentiment_matching\":true,\"skip_adhoc_email_sends\":false,\"android_enable_draft_notes\":true,\"permalink_reply_ranking_variant\":\"experiment\",\"desktop_live_stream_participant_labels\":false,\"allow_feed_category_filtering\":false,\"universal_feed_translator_experiment\":\"experiment\",\"enable_livestream_screenshare_detection\":true,\"private_live_streaming_enabled\":true,\"android_scheduled_notes_enabled\":true,\"portal_ranking_variant\":\"experiment\",\"desktop_live_stream_safe_framing\":0.8,\"enable_note_scheduling\":true,\"ios_limit_related_notes_in_permalink\":\"control\"},\"publicationSettings\":{\"block_ai_crawlers\":false,\"credit_token_enabled\":true,\"custom_tos_and_privacy\":false,\"did_identity\":\"did:plc:es3srknleppmlecmx45g2hoe\",\"disable_optimistic_bank_payments\":false,\"display_welcome_page_details\":true,\"enable_meetings\":false,\"payment_pledges_enabled\":true,\"enable_drop_caps\":false,\"enable_post_page_conversion\":false,\"enable_prev_next_nav\":true,\"enable_restacking\":true,\"gifts_from_substack_disabled\":false,\"google_analytics_4_token\":null,\"group_sections_and_podcasts_in_menu_enabled\":false,\"live_stream_homepage_visibility\":\"contributorsAndAdmins\",\"live_stream_homepage_style\":\"banner\",\"live_stream_replay_enabled\":true,\"medium_length_description\":\"The AI Engineer newsletter + Top 10 US Tech podcast + Community. Interviews, Essays and Guides on frontier LLMs, AI Infra, Agents, Devtools, UX, Open Models. See https://latent.space/about for highlights from Chris Lattner, Andrej Karpathy, George Hotz, Simon Willison, Soumith Chintala, et al!\",\"notes_feed_enabled\":false,\"paywall_unlock_tokens\":false,\"post_preview_crop_gravity\":\"auto\",\"post_preview_radius\":\"xs\",\"reader_referrals_enabled\":true,\"reader_referrals_leaderboard_enabled\":true,\"seen_coming_soon_explainer\":false,\"seen_google_analytics_migration_modal\":false,\"local_currency_modal_seen\":true,\"local_payment_methods_modal_seen\":true,\"twitter_pixel_signup_event_id\":null,\"twitter_pixel_subscribe_event_id\":null,\"use_local_currency\":true,\"welcome_page_opt_out_text\":\"No thanks\",\"cookie_settings\":\"\",\"show_restacks_below_posts\":true,\"holiday_gifting_post_header\":true,\"homepage_message_text\":\"\",\"homepage_message_link\":\"\",\"about_us_author_ids\":\"\",\"archived_section_ids\":\"\",\"column_section_ids\":\"\",\"fp_primary_column_section_ids\":\"\",\"event_section_ids\":\"\",\"podcasts_metadata\":\"\",\"video_section_ids\":\"\",\"post_metering_enabled\":false,\"use_custom_theme\":false},\"publicationUserSettings\":null,\"userSettings\":{\"user_id\":null,\"activity_likes_enabled\":true,\"dashboard_nav_refresh_enabled\":false,\"hasDismissedSectionToNewsletterRename\":false,\"is_guest_post_enabled\":true,\"feed_web_nux_seen_at\":null,\"has_seen_select_to_restack_tooltip_nux\":false,\"invite_friends_nux_dismissed_at\":null,\"suggestions_feed_item_last_shown_at\":null,\"has_seen_select_to_restack_modal\":false,\"last_notification_alert_shown_at\":null,\"disable_reply_hiding\":false,\"newest_seen_chat_item_published_at\":null,\"explicitContentEnabled\":false,\"contactMatchingEnabled\":false,\"messageRequestLevel\":\"everyone\",\"liveStreamAcceptableInviteLevel\":\"everyone\",\"liveStreamAcceptableChatLevel\":\"everyone\",\"creditTokensTreatmentExposed\":false,\"appBadgeIncludesChat\":false,\"autoPlayVideo\":true,\"smart_delivery_enabled\":false,\"chatbotTermsLastAcceptedAt\":null,\"has_seen_notes_post_app_upsell\":false,\"substack_summer_nux_dismissed_at\":null,\"first_note_id\":null,\"show_concurrent_live_stream_viewers\":false,\"has_dismissed_fp_download_pdf_nux\":false,\"edit_profile_feed_item_dismissed_at\":null,\"mobile_permalink_app_upsell_seen_at\":null,\"new_user_checklist_enabled\":false,\"new_user_follow_subscribe_prompt_dismissed_at\":null,\"has_seen_youtube_shorts_auto_publish_announcement\":false,\"has_seen_publish_youtube_connect_upsell\":false,\"notificationQualityFilterEnabled\":true,\"hasSeenOnboardingNewslettersScreen\":false,\"bestsellerBadgeEnabled\":true,\"hasSelfIdentifiedAsCreator\":false,\"autoTranslateEnabled\":true,\"autoTranslateBlocklist\":[]},\"subscriberCountDetails\":\"hundreds of thousands of subscribers\",\"mux_env_key\":\"u42pci814i6011qg3segrcpp9\",\"persona_environment_id\":\"env_o1Lbk4JhpY4PmvNkwaBdYwe5Fzkt\",\"sentry_environment\":\"production\",\"launchWelcomePage\":false,\"pendingInviteForActiveLiveStream\":null,\"isEligibleForLiveStreamCreation\":true,\"webviewPlatform\":null,\"noIndex\":false,\"post\":{\"audience\":\"everyone\",\"audience_before_archived\":null,\"canonical_url\":\"https://www.latent.space/p/harness-eng\",\"default_comment_sort\":null,\"editor_v2\":false,\"exempt_from_archive_paywall\":false,\"free_unlock_required\":false,\"id\":193478192,\"podcast_art_url\":null,\"podcast_duration\":4362.841,\"podcast_preview_upload_id\":null,\"podcast_upload_id\":\"bac92fb4-46a2-4c8a-b189-083c263423fd\",\"podcast_url\":\"https://api.substack.com/api/v1/audio/upload/bac92fb4-46a2-4c8a-b189-083c263423fd/src\",\"post_date\":\"2026-04-07T17:14:26.942Z\",\"updated_at\":\"2026-04-07T17:24:40.647Z\",\"publication_id\":1084089,\"search_engine_description\":null,\"search_engine_title\":null,\"section_id\":null,\"should_send_free_preview\":false,\"show_guest_bios\":true,\"slug\":\"harness-eng\",\"social_title\":null,\"subtitle\":\"We shed light on OpenAI's first Dark Factory for the first time.\",\"teaser_post_eligible\":true,\"title\":\"Extreme Harness Engineering for Token Billionaires: 1M LOC, 1B toks/day, 0% human code, 0% human review \u2014 Ryan Lopopolo, OpenAI Frontier & Symphony\",\"type\":\"podcast\",\"video_upload_id\":null,\"write_comment_permissions\":\"everyone\",\"meter_type\":\"none\",\"live_stream_id\":null,\"is_published\":true,\"restacks\":2,\"reactions\":{\"\u2764\":42},\"top_exclusions\":[],\"pins\":[],\"section_pins\":[],\"has_shareable_clips\":false,\"previous_post_slug\":\"pmarca\",\"next_post_slug\":\"notion\",\"cover_image\":\"https://substack-video.s3.amazonaws.com/video_upload/post/193478192/bac92fb4-46a2-4c8a-b189-083c263423fd/transcoded-1775581604.png\",\"cover_image_is_square\":false,\"cover_image_is_explicit\":false,\"podcast_episode_image_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/534f41b9-5d2b-49b9-9578-4852473c362f_1400x1400.png\",\"podcast_episode_image_info\":{\"url\":\"https://substack-post-media.s3.amazonaws.com/public/images/534f41b9-5d2b-49b9-9578-4852473c362f_1400x1400.png\",\"isDefaultArt\":false,\"isDefault\":false},\"videoUpload\":null,\"podcastFields\":{\"post_id\":193478192,\"podcast_episode_number\":null,\"podcast_season_number\":null,\"podcast_episode_type\":null,\"should_syndicate_to_other_feed\":null,\"syndicate_to_section_id\":null,\"hide_from_feed\":false,\"free_podcast_url\":null,\"free_podcast_duration\":null,\"preview_contains_ad\":false},\"podcastUpload\":{\"id\":\"bac92fb4-46a2-4c8a-b189-083c263423fd\",\"name\":\"2Latent Space_ Ryan Lopoplo (OpenAI) on Harness Engineering, Symphony & Frontier.mp3\",\"created_at\":\"2026-04-07T16:54:04.935Z\",\"uploaded_at\":\"2026-04-07T16:54:32.619Z\",\"publication_id\":1084089,\"state\":\"transcoded\",\"post_id\":193478192,\"user_id\":89230629,\"duration\":4362.841,\"height\":null,\"width\":null,\"thumbnail_id\":1775581604,\"preview_start\":null,\"preview_duration\":null,\"media_type\":\"audio\",\"primary_file_size\":52357357,\"is_mux\":false,\"mux_asset_id\":null,\"mux_playback_id\":null,\"mux_preview_asset_id\":null,\"mux_preview_playback_id\":null,\"mux_rendition_quality\":null,\"mux_preview_rendition_quality\":null,\"explicit\":false,\"copyright_infringement\":null,\"src_media_upload_id\":null,\"live_stream_id\":null,\"transcription\":{\"media_upload_id\":\"bac92fb4-46a2-4c8a-b189-083c263423fd\",\"created_at\":\"2026-04-07T16:55:48.336Z\",\"requested_by\":89230629,\"status\":\"transcribed\",\"modal_call_id\":\"fc-01KNMDY9PE43TJE5K3K2M98HQQ\",\"approved_at\":\"2026-04-07T16:59:29.699Z\",\"transcript_url\":\"s3://substack-video/video_upload/post/193478192/bac92fb4-46a2-4c8a-b189-083c263423fd/1775580954/transcription.json\",\"attention_vocab\":null,\"speaker_map\":null,\"captions_map\":{\"en\":{\"url\":\"s3://substack-video/video_upload/post/193478192/bac92fb4-46a2-4c8a-b189-083c263423fd/1775580954/en.vtt\",\"language\":\"en\",\"original\":true}},\"cdn_url\":\"https://substackcdn.com/video_upload/post/193478192/bac92fb4-46a2-4c8a-b189-083c263423fd/1775580954/transcription.json?Expires=1776777264&Key-Pair-Id=APKAIVDA3NPSMPSPESQQ&Signature=JgQPOevgILsD0x3v3jFGQM1vPpD8q44Pc2KBS5Y8QqwQ~TzKgRUIPORpQmzMDQSwW8XSYfL-NS3W4njncpPo21yg~ibaURVuQofu7uKRhMvu05NEhqpr7~-C5Z9GdR3dTlgapinNnj7TG0U8k3TE1LruAlm7GoOU2mhjaTbSXfZynYMGpodcOSLg-37IuJNpUDrq6xcChvKChgq8T2hzL4Np4~k1nmLjj5WSSXjQ0OpBLbgBP-S1HPhwKfCvi8JJQURcmZa6MO4-x4IgYui-k9JjkUdkYqeQQgjx3eIq96uRC0E8WzDi1jTYOl0J59hB~mJdBzSWKd3DgsVxX5yr-g__\",\"cdn_unaligned_url\":\"https://substackcdn.com/video_upload/post/193478192/bac92fb4-46a2-4c8a-b189-083c263423fd/1775580954/unaligned_transcription.json?Expires=1776777264&Key-Pair-Id=APKAIVDA3NPSMPSPESQQ&Signature=Umd6bWW~yLK8moTk6W-q5Ms4Ib~7raOqw-xetKFSGN77nYQ0A6Cdsyo6~xn-NM-ENEnHsQO95ex2bOJBkSyQGoFlJbYOZehH2ZCJ2b6-J56ajmUFRA6YpHJGfCn4rxoHWMZs2CkM8tDWeR3n9WcE9iBiGcvywqYEF7r5TMBt4cbh~4uKXZQOR7-bI3ZnfoCRFoO4nBobJnpwcR5fmf0GeksFQ~4O3qFc8UX56g3qVBc5Ahrf5ObGzHzsMlC45IanRg1M7fzHlo-hrXpxmYUB5iQUAvb5kKyqOa50BrUYA34nhfuY~9a2JRCPN~Y9cAJ0f4UMh0f21C9HxRKZt8GqAw__\",\"signed_captions\":[{\"language\":\"en\",\"url\":\"https://substackcdn.com/video_upload/post/193478192/bac92fb4-46a2-4c8a-b189-083c263423fd/1775580954/en.vtt?Expires=1776777264&Key-Pair-Id=APKAIVDA3NPSMPSPESQQ&Signature=UZMXVQNRECXQWo7~o1sp2SYszf~O8EBMcxLBvGc0ZU3l7a-ouYRRrnRbNp-TjdV6cx1tAITjD3rzP4EPXBqoOVMJvYNKTuG-LdZmrU8XlQsX4tqzT0QtFOFf9e3lR7HqjefPJcV6-8QIoQxwCRF23rIKg7ew1iTEfPWEyIJpjAY2WhBYxXkqk--6PnjRM6hihSPkAo1I~izL0mIE5SpEVdxeXfH53oyMcHXM3g1S7n~q~w~WcrQaonjneC6XuTVZN7JkenbN1rT36aOKApUYmylhaGNzUZRhp56-uzFdMyOJ7KYbF2oNChtURW97Aumr4ESOlCTFzs~9mOemLl3QDQ__\",\"original\":true}]}},\"podcastPreviewUpload\":null,\"voiceover_upload_id\":null,\"voiceoverUpload\":null,\"has_voiceover\":false,\"description\":\"We shed light on OpenAI's first Dark Factory for the first time.\",\"body_html\":\"
We\u2019re proud to release this ahead of Ryan\u2019s keynote at AIE Europe. Hit the bell, get notified when it is live! Attendees: come prepped for Ryan\u2019s AMA with Vibhu after.

Move over, context engineering. Now it\u2019s time for Harness engineering and the age of the token billionaires.

Ryan Lopopolo of OpenAI is leading that charge, recently publishing a lengthy essay on Harness Eng that has become the talk of the town:

fuller discussion between Bret and Ryan
In it, Ryan peeled back the curtains on how the recently announced OpenAI Frontier team have become OpenAI\u2019s top Codex users, running a >1m LOC codebase with 0 human written code and, crucially for the Dark Factory fans, no human REVIEWED code before merge. Ryan is admirably evangelical about this, calling it borderline \u201Cnegligent\u201D if you aren\u2019t using >1B tokens a day (roughly $2-3k/day in token spend based on market rates and caching assumptions):

search it
Over the past five months, they ran an extreme experiment: building and shipping an internal beta product with zero manually written code. Through the experiment, they adopted a different model of engineering work: when the agent failed, instead of prompting it better or to \u201Ctry harder,\u201D the team would look at \u201Cwhat capability, context, or structure is missing?\u201D

The result was Symphony, \u201Ca ghost library\u201D and reference Elixir implementation (by Alex Kotliarskyi) that sets up a massive system of Codex agents all extensively prompted with the specificity of a proper PRD spec, but without full implementation:

The future starts taking shape as one where coding agents stop being copilots and start becoming real teammates anyone can use and Codex is doubling down on that mission with their Superbowl messaging of \u201Cyou can just build things\u201D.

Across Codex, internal observability stacks, and the multi-agent orchestration system his team calls Symphony, Ryan has been pushing what happens when you optimize an entire codebase, workflow, and organization around agent legibility instead of human habit.

We sat down with Ryan to dig into how OpenAI\u2019s internal teams actually use Codex, why the real bottleneck in AI-native software development is now human attention rather than tokens, how fast build loops, observability, specs, and skills let agents operate autonomously, why software increasingly needs to be written for the model as much as for the engineer, and how Frontier points toward a future where agents can safely do economically valuable work across the enterprise.

We discuss:

Ryan\u2019s background from Snowflake, Brex, Stripe, and Citadel to OpenAI Frontier Product Exploration, where he works on new product development for deploying agents safely at enterprise scale

The origin of \u201Charness engineering\u201D and the constraint that kicked off the whole experiment: Ryan deliberately refused to write code himself so the agent had to do the job end to end

Building an internal product over five months with zero lines of human-written code, more than a million lines in the repo, and thousands of PRs across multiple Codex model generations

Why early Codex was painfully slow at first, and how the team learned to decompose tasks, build better primitives, and gradually turn the agent into a much faster engineer than any individual human

The obsession with fast build times: why one minute became the upper bound for the inner loop, and how the team repeatedly retooled the build system to keep agents productive

Why humans became the bottleneck, and how Ryan\u2019s team shifted from reviewing code directly to building systems, observability, and context that let agents review, fix, and merge work autonomously

Skills, docs, tests, markdown trackers, and quality scores as ways of encoding engineering taste and non-functional requirements directly into context the agent can use

The shift from predefined scaffolds to reasoning-model-led workflows, where the harness becomes the box and the model chooses how to proceed

Symphony, OpenAI\u2019s internal Elixir-based orchestration layer for spinning up, supervising, reworking, and coordinating large numbers of coding agents across tickets and repos

Why code is increasingly disposable, why worktrees and merge conflicts matter less when agents can resolve them, and what it really means to fully delegate the PR lifecycle

\u201CGhost libraries\u201D, spec-driven software, and the idea that a coding agent can reproduce complex systems from a high-fidelity specification rather than shared source code

The broader future of Frontier: safely deploying observable, governable agents into enterprises, and building the collaboration, security, and control layers needed for real-world agentic work

Ryan Lopopolo

X: https://x.com/_lopopolo

Linkedin: https://www.linkedin.com/in/ryanlopopolo/

Website: https://hyperbo.la/contact/

## Timestamps

00:00:00 Introduction: Harness Engineering and OpenAI Frontier
00:02:20 Rya