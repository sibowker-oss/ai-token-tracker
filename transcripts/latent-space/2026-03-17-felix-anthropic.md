# Why Anthropic Thinks AI Should Have Its Own Computer — Felix Rieseberg of Claude Cowork & Claude Code Desktop

**Source:** Latent Space  
**Date:** 2026-03-17  
**URL:** https://www.latent.space/p/felix-anthropic  
**Tier:** 1  

---

Claude Cowork came out of an accident.

Felix and the Anthropic team noticed something interesting with Claude Code: many users were using it primarily for all kinds of messy knowledge work instead of coding. Even technical builders would use it for lots of non-technical work.

Felix Rieseberg@felixrieseberg
Claude Code doesn't just resonate with developers anymore. Non-technical people are using it to build things. Technical people are using it for non-technical work. The line is blurring.

I'm by far not the first to think about this. Multiple teams at Anthropic have been working1:12 AM · Jan 13, 2026 · 321K Views88 Replies · 148 Reposts · 1.72K Likes
Even more shocking, Claude cowork wrote itself. With a team of humans simply orchestrating multiple claude code instances, the tool was ready after a brief week and a half.

This isn’t Felix’s first rodeo with impactful and playful desktop apps. He’s helped ship the Slack desktop app and is a core maintainer of Electron the open-source software framework used for building cross-platform desktop applications, even putting Windows 95 into an Electron app that runs on macOS, Windows, and Linux.
github.com/felixrieseberg…</a> ","username":"felixrieseberg","name":"Felix Rieseberg","profile_image_url":"https://pbs.substack.com/profile_images/1544558915819487233/qMrauBqx_normal.jpg","date":"2018-08-23T14:54:03.000Z","photos":[{"img_url":"https://pbs.substack.com/media/DlSuLBJVsAAFs8r.jpg","link_url":"https://t.co/YquOnOGrSz"}],"quoted_tweet":{},"reply_count":474,"retweet_count":5615,"like_count":16045,"impression_count":0,"expanded_url":null,"video_url":null,"belowTheFold":false}" class="pencraft pc-display-flex pc-flexDirection-column pc-gap-12 pc-padding-16 pc-reset bg-primary-zk6FDl outline-detail-vcQLyr pc-borderRadius-md sizing-border-box-DggLA4 pressable-lg-kV7yq8 font-text-qe4AeH tweet-fWkQfo twitter-embed">
Felix Rieseberg@felixrieseberg
I put Windows 95 into an Electron app that now runs on macOS, Windows, and Linux. It's a terrible idea that works shockingly well. I'm so sorry.

Go grab it here: github.com/felixrieseberg… 2:54 PM · Aug 23, 2018474 Replies · 5.62K Reposts · 16K Likes
In this episode, Felix joins us to unpack why execution has suddenly become cheap enough that teams can “just build all the candidates” and why the real frontier in AI products is no longer better chat, but trusted task execution.

He also shares why Anthropic is betting on local-first agent workflows, why skills may matter more than most people realize, and how the hardest questions ahead are about autonomy, safety, portability, and the changing shape of knowledge work itself.

## We discuss

Felix’s path: Slack desktop app, Electron, Windows 95 in JavaScript, and now building Claude Cowork at Anthropic

What Claude Cowork actually is: a more user-friendly, VM-based version of Claude Code designed to bring agentic workflows to non-terminal-native users

https://news.ycombinator.com/item?id=47220118

Why “user-friendly” does not mean “less powerful”: Cowork as a superset product, much like how VS Code initially looked simpler than Visual Studio but became more hackable and extensible

Anthropic’s prototype-first culture: why Cowork was built in 10 days using many pre-existing internal pieces, and how internal prototypes shaped the final product

Why execution is getting cheap: the shift from long memos, specs, and debate toward rapidly building multiple candidates and choosing based on reality instead of theory

The local debate: why Felix thinks Silicon Valley is undervaluing the local computer, and why putting Claude “where you work” is often more powerful

Why Claude gets its own computer: the VM as both a safety boundary and a capability unlock, letting Claude install tools, run scripts, and work more independently without constant approval

Safety through sandboxing: why “approve every command” is not a real long-term UX, and how virtual machines create a middle ground between uselessly safe and dangerously autonomous

How Cowork differs from Claude Code: coding evals vs. knowledge-work evals, different system-prompt tradeoffs, longer planning horizons, and heavier use of planning and clarification tools

Why skills matter: simple markdown-based instructions as a lightweight abstraction layer for reusable workflows, personalized automation, and portable agent behavior

Skills vs. MCPs: why Felix is increasingly interested in file-based, text-native interfaces that tell the model what to do, rather than forcing everything through rigid tool schemas

The portability problem: why personal skills should move across agent products, and the unresolved tension between public reusable workflows and private user-specific context

Real use cases already happening today: uploading videos, organizing files, handling taxes, managing calendars, debugging internal crashes, analyzing finances, and automating repetitive browser workflows

Claude@claudeai
In Cowork, you give Claude access to a folder on your computer. Claude can then read, edit, or create files in that folder.

Try it to create a spreadsheet from a pile of screenshots, or produce a first draft from scattered notes. 8:06 PM · Jan 12, 2026 · 7.13M Views264 Replies · 888 Reposts · 12.2K Likes
Why AI products should work with your existing stack: Anthropic’s bias toward integrating with Chrome, Office, and existing workflows instead of rebuilding every app from scratch

Felix Rieseberg@felixrieseberg
Shipping today: Small but meaningful updates to Claude in Excel & PowerPoint!

We obviously want Claude to be helpful in your work lives across a wide range of apps and data - and with this change, PowerPoint & Excel can share context and gain support for Skills.8:05 PM · Mar 11, 2026 · 29K Views19 Replies · 27 Reposts · 474 Likes
Computer use one year later: how much better it has gotten, why vision plus browser context is such a superpower, and why letting Claude see the thing it is working on changes everything

Why many “AI verticals” may get compressed: specialized wrappers may matter in the short term, but better general models and stronger primitives could absorb a lot of narrow use cases

The future of junior work: Felix’s concerns about entry-level roles, labor-market disruption, and whether AI can compress early-career learning into denser simulated experience

Why Waterloo grads stand out: internships, shipping experience, and learning how real teams build products versus purely theoretical academic preparation

The agentic future of the desktop: what it means for Claude to have its own computer, whether AI should act on your machine or a remote one, and how intimacy with personal data changes the product design space

Why Electron still mattered: shipping Chromium as a controlled rendering stack, the limits of OS-native webviews, and why browser engines remain one of the great software abstractions
@electronjs</span> into just 55 pages.\n\nThanks to <span class=\"tweet-fake-link\">@OReillyMedia</span>'s great <span class=\"tweet-fake-link\">@allymacdonald</span>, it's now a pretty solid read!\n\n<a class=\"tweet-url\" href=\"https://www.safaribooksonline.com/library/view/introducing-electron/9781491996041/\">safaribooksonline.com/library/view/i…</a> ","username":"felixrieseberg","name":"Felix Rieseberg","profile_image_url":"https://pbs.substack.com/profile_images/1544558915819487233/qMrauBqx_normal.jpg","date":"2017-12-11T18:34:15.000Z","photos":[{"img_url":"https://pbs.substack.com/media/DQyRXazU8AAEmIG.jpg","link_url":"https://t.co/xKYYtH82NC"}],"quoted_tweet":{},"reply_count":3,"retweet_count":28,"like_count":107,"impression_count":0,"expanded_url":null,"video_url":null,"belowTheFold":true}" class="pencraft pc-display-flex pc-flexDirection-column pc-gap-12 pc-padding-16 pc-reset bg-primary-zk6FDl outline-detail-vcQLyr pc-borderRadius-md sizing-border-box-DggLA4 pressable-lg-kV7yq8 font-text-qe4AeH tweet-fWkQfo twitter-embed">
Felix Rieseberg@felixrieseberg
✨ 📚 I wrote a short book! I spent weeks squeezing the most important "getting started" knowledge about building desktop apps with @electronjs into just 55 pages.

Thanks to @OReillyMedia's great @allymacdonald, it's now a pretty solid read!

safaribooksonline.com/library/view/i… 6:34 PM · Dec 11, 20173 Replies · 28 Reposts · 107 Likes
Anthropic’s Labs mentality: wild internal experiments, half-broken future-looking prototypes, and the broader effort to move users from asking questions to delegating increasingly long and valuable tasks

Why the endgame is not just more capability, but more independence: teaching users to trust AI with bigger scopes of work, for longer durations, with fewer interventions

## Felix Rieseberg

X: https://x.com/felixrieseberg

LinkedIn: https://www.linkedin.com/in/felixrieseberg

Website: https://felixrieseberg.com/

## Anthropic

Website: http://anthropic.com

## Full Video Pod

## Timestamps

00:00 — Cheap execution and building all the candidates
00:44 — Intro in the new Kernel studio
02:47 — What Claude Cowork is
04:18 — Why user-friendly can be more powerful
05:33 — How Anthropic built Cowork
07:09 — Prototype-first product development
08:00 — Why local computers still matter
09:20 — Skills, primitives, and platform leverage
12:13 — Cowork’s architecture: VM + Chrome + system prompt
15:38 — Felix’s own bug-fixing Cowork workflows
17:38 — Local-first agents
20:16 — Evals, planning, and knowledge-work optimization
23:14 — What Anthropic means by evals
24:21 — Scaffolding, tools, and why skills matter
27:44 — Demo: YouTube uploads and self-generated skills
31:03 — Calendar automation and cleaning your desktop
34:47 — Browser context and why DOM access matters
37:47 — Skills portability and plugins
44:36 — Which AI categories survive?
46:19 — Junior jobs, simulated work, and labor disruption
52:00 — Gradual takeoff vs big-bang takeoff
53:42 — Finance, taxes, and enterprise verticals
56:24 — Vision and the improvement in computer use
57:31 — Why Claude writes its own scripts
58:06 — Should Claude have its own computer?
1:01:26 — Windows 95 in JavaScript
1:03:19 — VM tradeoffs and sandbox design
1:07:23 — Approval fatigue and safe delegation
1:11:18 — The future of Cowork
1:12:27 — What comes next for agentic knowledge work
1:15:13 — Electron, Chromium, and desktop software lessons
1:22:16 — Multiplayer agents and coworker-to-coworker workflows
1:26:05 — Anthropic Labs and closing thoughts

## Transcript

Alessio: Hey everyone. Welcome to the Latent Space Podcast, our first one in the new studio. This is Alessio, founder of Kernel Labs, and I’m joined by swyx, editor of Latent Space.

swyx: Yeah, so nice to be here. Thanks to, uh, TJ, Alessio, Allen helping to set everything up. It looks beautiful. We even have the logo outside.

Yeah, kind.

Felix: It’s like really nice, right? When you walk in here as a guest, you’re like, ah, this is a serious production. You’re like, feel it immediately.

swyx: Yeah. Felix, you’ve been, you’re, you’re currently a product manager of Cowork or,

Felix: uh, really Technic

swyx: Eng. Yeah. The, the identities are kind of vague member technical staff.

Felix: I know member staff is like, the official title will carry around forever.

swyx: Yeah. I basically kind of wanted, like we’ve been. Kinda obsessed. I, I’ve been using it a lot, even for managing latent space. Like, uh, cowork helps me upload videos and like title things and like edit and everything. It’s, it’s like really amazing.

Alessio: Cool. He said multiple times Cowork has said gi in the group track.

swyx: Yeah, yeah, yeah. So, so we have a second, uh, we have a second channel, uh, for latent space tv. Uh, and I, uh, and uh, we basically, this is our Discord meetup. Um, and I I, we have like Claude Coworks, it might be a GI, I don’t know if we, we have, uh, uploaded it yet, but one of the sessions was like a, like a Claude cowork thing.

Felix: I, you have to see, I would love to see it. Like, I’m so curious, like one of the most fun parts of my job is like constantly see the weird things people use Cowork for because it’s obviously like very hard for us to actually design for specific use cases we do. But like every single person who’s like most amazed is usually amazed about a thing that I didn’t even expect cowork would be good at.

Um, we have a new designer and it’s one of the first small tasks. I was like, Hey, we need like a new emoji for cowork for our internal stock. It’s like a pretty small thing. I like, can you please do it? And he drew an SVG and just gave it to coworker was like, can you animate this emoji? And now it has like this beautiful loopy animation.

Um, and I mean, I think obviously this goes down to like, it turns out you can do more things with code than you expected, but it, it’s like that kind of stuff that is really fun to me. So, long story short, I would love to see like, the kind of things you’re doing.

swyx: I’ll pull it up. I’ll pull it up.

Felix: Yeah. Yeah.

swyx: Uh, but before we get into it, I, I think always wanna start with like a top level. What is Claude Cowork for people who haven’t heard of it? Haven’t tried it out.

Felix: Okay. Uh, real quick, Claude Cowork is a user friendly version of Claude Code. So the way it basically works is we have Claude Code and for us, fairly impressive agent harness that over December we noticed more and more people are using either, even though they’re not technical, they, they’re not at home in the terminal or they are at home in the terminal, but they started using Claude Code for non-coding workloads, right?

Like managing expenses or like filling out receipts or organizing a knowledge base. Like there was a big obsidian moment that a lot of people liked and we wanted to capitalize on that, but also bring, bring this capability to people who are not terminal native and who might not know how to like brew and store something.

So cowork is Claude Code running in original machine with a little bit of padding, a little bit more guardrails, making it a little safer and a little bit more convenient for people who don’t wanna first open up the terminal when they go to work.

swyx: It’s interesting, uh, that is kind of. Pitch that way as a more user friendly thing because I always feel like it, it, to me, I I treat it as like why I’m familiar with Claude Code.

Like we, we did a Claude Code episode Yeah. A year ago. But this one is like even more power user tools ‘cause it, uh, it kind of integrates much better with like clotting Chrome and, uh, in all the, all the other tooling. But like, maybe, maybe that’s like a perception thing, right? Like

Felix: No, honestly, I don’t think you’re wrong.

This is like a, a thing I’ve been thinking a lot about for like the last two weeks. So,

swyx: but when they say user friendly, it’s like, oh, it’s the dumb down version. But no, actually this is the superset.

Felix: Yeah. Like, I think a similar thing happened, A similar thing happened to me about 10 years ago, like maybe 12 years ago when I was at Microsoft and we started working on, on Electron and like browser-based technologies and cross-platform stuff.

And one of the first use cases was Visual Studio Code, which used to be a website. And the initial narrative was, or Visual Studio Code is, is like a more user-friendly version of Visual Studio. But in a similar vein, I think there was some voices saying, oh, this is. For serious developers, like, we’re not gonna use this.

Right? For like anything. And I think in the end what happened is people have different stories about why Visual Studio Code became such a big thing. But my personal, my personal belief is that the Hackability and the extendability has like played a pretty big role, right? You can hook in Visual Studio Code that like almost any workload, it’s so easy to hack on, so easy to put extensions for it.

And I think cowork might be hitting a similar thing where it’s very easy to extend and it’s very easy to bring into your workflows. Uh, so the convenience I think is a bit of a, it’s obviously the thing we strive for as developers, but I think the way people find value in it then is by probably mapping it onto whatever they actually have to do in their job.

Alessio: So end of last year, you see the spike of like non-technical usage and clock code. What’s the design process to say we should make clock code work? Because I mean, you built it in only 10 days. Um, I’m sure there was some discussion before on whether it’s easier to use mean. You know, like making, making like a desktop GUI is obviously one way to do it, but like there’s a lot of nuance in the product.

Like maybe talk people through what was like the trigger of like, we should build a separate thing. We should not build like a different plot code thing. And then maybe some of the more interesting design decisions that maybe you didn’t take.

Felix: Yeah, I think philanthropic, we’ve been thinking about ways to move people who are comfortable with using Claude to answer questions and bring more of the power of like this thing to now like, execute tasks for you.

I can like solve problems for you can like build things for you. How do we bring that capability to people who are currently mostly comfortable with like a like question answer paradigm within the chat. And we’ve had a lot of prototypes around that. Just going back as far as like easily a year and a half.

Like we had a lot of people working on that. Um, and internally philanthropic is a very prototype demo, first culture. We have a lot of like internal prototypes that don’t reach the public. What Cowork actually became is like we sort of picked the right pieces out of the many prototypes that we had.

Right. And that’s, that’s maybe also like, I think an important qualifier whenever people mention this like 10 day number. I do think it’s important to me to mention that within Double Scratch there was like a lot of stuff already happening, right? Like, and I think it’s important for people to remember that when you build a website, you use React, you use like a bunch of other things.

And this is like a similar scenario with like a lot of pieces we already had. Um, and in terms of decision path, I think we live in like an interesting new world where execution is actually quite cheap.

swyx: Mm-hmm.

Felix: So maybe, maybe what you would do That’s so crazy. The year. I know it’s wild.

swyx: You should be, ideas are cheap.

Execution is the hard part. I

Felix: know. And like the, we, we used to live in this world maybe where you would take a product manager and the product manager would go to a number of potential customers and in this like very low bandwidth way, would try to. Try to like tease out what are the problems they’re having, what are they willing to buy?

Um, and then maybe what can you build to like drive out that need and then you go back and you like draft a spec and you think about it and then like you make a design and you execute it. We internally philanthropic app, not pretty much closer to the point where we’re like, don’t even write a memo, just like build, like let’s build all the candidates very quickly.

Let’s just build all of them and then pick the best ones. I think the, the decision that is most impactful both for the product as well for the users right now is like the way we put value on your local computer. I think that’s a big decision point a lot of people have thought about. Should this thing, whatever it is, should it ultimately run into computer or should it run in the cloud?

‘cause they’re big trade offs, right?

Alessio: I guess like if we solve auth, it would be easy to do in the cloud. But I think like the fact that I can just download any file from anywhere and then put it and cowork there, it’s like a big unlock. Um, I mean it’s interesting you mentioned reusing certain pieces. I think this is something I’ve been thinking about even with Claude Code, right?

The price of like writing code is going to zero, blah, blah, blah. But it actually seems like the value of having some sort of platform substrate is like increasing because as you build these new things, you can kind of plug them together.

Felix: Yeah.

Alessio: So I almost feel like when people are saying, oh, the value of a lot of software is gonna zero because you can recreate it, to me it’s almost like the opposite.

It’s like having an existing platform to build on top of. It’s like even more valuable because you can kind of bolt things on.

Felix: Yeah.

Alessio: You have obviously mcps, you have skills, you have like obviously the models, which is a big part. All these things kind of come together. Do you feel like that’s a valid way to think about it, where people should invest even more in kind of like primitives.

To rebuild on or are you like recreating a lot of it each time because like things change and it’s easier to rewrite than reuse?

Felix: You know, I think, I think you’re right. I think you’re right that the holistic platform is really useful. And this is maybe a whole like a somewhat contrarian view to a lot of people in ai.

I actually don’t think that the future is going to be hyper personalized software down to the point where everyone is running their own version. Like, I actually think it’s going to be quite hard for all of us to have our own internal chat tool and like, if I wanna talk to you, like

swyx: how

Felix: is that gonna work, right?

In the, in the context of cowork and how we build it, I think it’s a bit of a combination. Like what the, the execution that gets cheap is not necessarily rebuilding all the primitives. I think our priori, there’s also not a lot of value in it. So for instance, my team did not think about rebuilding clock code.

We’re like very much started with the. The core thesis of this should be Claude Code.

Mm-hmm.

Felix: And then we’ll like build things on top of it. The part of the execution that gets a little cheaper is like, how do you take all of these Lego pieces and put them together in a way that makes sense for users?

It’s like actually valuable. You have so many different approaches now in terms of what kind of, what kind of things do you actually elevate to a primitive, do you strongly believe that all your products should be built by just combining primitive that the public also has available? Do you keep some things internal?

Um, and I think that’s still evolving, but I think what’s probably gonna go away is like, I’m not sure if it’s gonna fully go away, but I’m gonna say, I think for me personally, I will probably no longer try to come up with a really good product without testing up with people. This is not a new concept, but wherever you used to have to make costly decisions around, do we pick technology A or technology B, or do we like, um, build it this way, build it the other way.

I really strongly believe now you just build all of them and try them out with a small focus group and then whatever, whatever is better is what you go with. Right. And that, that is probably quite different even from how we maybe worked a year ago. Right. Like, I think, I think this happened very recently.

Alessio: Yeah. I started building something in on Electron since you’re here. Coincidence. Uh, but then Electron and like SQL Light are like, there’s like some issues that like between development and like, uh, building anyway. And I was like, let’s just rebuild the whole thing in Swift and just recreated the whole thing in Swift.

And it’s like, I. It’s done.

swyx: You know, I didn’t take any effort. I, I, I don’t even know Swift.

Alessio: Yeah, exactly. I was like, I’m the, I’m not reviewing it anyway, whatever. You can write in whatever language you pick, but the important stuff that I did was not write the electron bindings. Yeah. It was like the logic of what happens in the app, you know, and then the model is like, yeah, I can just recreate the same thing as with

swyx: Yeah.

I, I think you still want, especially for people who are doing like high performance software or like very complex software, uh, you still want like, some view of the architecture. Uh, but you can use markdown for that,

Felix: right? Yeah.

swyx: Uh, you don’t actually have to read the code again. I, I’m still like on a sort of like a definitional thing.

Um, can we build a good mental model of Claude Cowork? Um, this is what I have, right? Like you you said it’s like fundamentally cloud co. We don’t wanna touch it. There’s the cloud app, there’s clouding Chrome. I think you guys do something different in planning, but, uh, I’ve been talking with Tariq who is on the cloud co team, and you guys are, he’s like, no, we just exposed planning.

Maybe we can clarify like, what are the major pieces. That people should be aware. It goes into cowork, like,

Felix: okay, I think you basically have them. So really, um, you can, you can take planning more or less out. I think there’s a few things that are really valuable in cowork. Um, the virtual machine is probably the most powerful thing.

So we currently run like a, we currently run like a lightweight VM and we put clocked out into the vm and we do that for, for, um, a number of reasons. Safety and security is a big one, but even if you, even if you ignore for a second safety and security and you’re just like, okay, Yolo, I want this thing to do whatever.

It is quite powerful to give Claus on computer that is like generally a good idea. And in terms of architecture and UX and everything else that we’ve been working on, philanthropic, it often is quite useful for you to like anthropomorphize, um, clot aggressively and just be like, this is a person. What will you do if you give a, if you had a person, right?

Yeah. And the analogy I’ve given my dad this morning who is still like quite insistent on using chat even for like coding things, is if you were a developer and your employer told you that you don’t need a computer, they’re just gonna like, send you emails with a code and you send emails with code back like that, maybe work for Patrick Miles in the back, but that it’s not very effective.

Um, so what we can do with the VM is because it’s a, it’s a Linux system, Claude Code has more or less free reign to install whatever needs to install. It can install Python, it can install no js. We do have strict network ingress and egress controls. So you can still, as, as a user in like plain human language, make it clear to, to the entire system what you’re okay with and what you’re not okay with.

But at no point do we have to ask a real person, like a, like a person who might be in marketing or a lawyer. I’d have to go to a lawyer and be like, are you okay with me installing Homebrew?

Alessio: Yeah, yeah.

Felix: Right. Because the implications of the question and the answer are complex and nuanced and like, not, not easy to reason about.

This gives us a lot of distraction that makes Cloud very powerful. Now then around it, we, we do probably have a number of things that also keeps growing almost every single week that you’re probably noticing that make cowork maybe better for certain tasks than just cloud. Cloud on its own. Yeah. But most of those actually live in the system prompt.

They’re about like, what can we infer about the work that you do? What can we, what can we intru in the system prompt to make that more effective? It’s of course the like very tight integration with Cloud and Chrome. You’re noticing that a lot of people, especially as the models get better, a lot of people throw up their hands when it comes to MCP connectors in this area.

I’m not gonna, I’m not gonna go through like 25 M CCP connectors, click off everywhere and then like half of them don’t let me do the things anyway. So Cloud and Chrome is quite powerful because we can just talk to the cloud and Chrome sub agent and that will just do things for you.

swyx: Yeah, so, so one example right in MCPI, honestly, I think that the state of MCP is kind of, kind of.

Really hard to integrate. Um, I need to, I needed to add, uh, Figma MCP to the coding agent that I use.

Felix: Yeah.

swyx: Uh, and, but I didn’t wanna read the docs, so I just had caught to it. And it’s, it’s great at reading docs and the same, same way I had to set up like a Google Cloud, um, account for some project I was working on and get some API keys somewhere.

And Google Cloud is famously super hard to navigate, so I just didn’t wanna deal with any of it. I just used Claude Cowork

Felix: within the first week of developing on Core. This happened very, very quickly. Um, I caught myself by starting to use cowork for coding tasks, which is not ostensibly what we built it for, right?

We don’t need to. But I found myself, um, I found myself like on our internal, internal tool that we have for, to collect crashes and just like debugging information and I found myself sort like picking out the ones that I think we can easily fix versus the ones that might be like kernel corruption or something else on the operating system.

And I found myself sort of picking these out and then just telling Clark, go fix this bug. I was like, what am I doing here? Go one level up, tell a cowork, I want you to go to all these crash tools. I want you to find all the bugs that you think are fixable and not like an operating system crash. And then I want you to tell another cloud to like fix all of that.

Um, and that’s, that’s, that’s sort of another cloud,

swyx: just so it can spin up another instance or,

Felix: uh, it, currently what I do is, um, and this is a bit of a hack, but I tell it to use clockwork remote to which website itself? Yeah, that’s interesting. So you basically take, if you, if you imagine like a dashboard with like 20 bucks, you, this is remote control or clock or remote, or, sorry, I just wanted to confirm what, the way I’m using it is.

I have cowork running and I’m telling cowork, here’s where I normally go every morning to find the latest bugs. Go read the entire bug list, separate out which ones are fixable, which ones are, are fixable, and then for the fixable ones, four is this almost loop. For each bug, write a markdown file with a prompt.

And then for each markdown v, that is a prompt. Start of a cloud set. So natively Claude Code has

swyx: this concept of subagents. Mm-hmm. And this is basically a subagent, but you’re not using the subagent functionality.

Felix: I’m not using the subagent functionality. And the reason I’m not is because I’m firing that off as a Claude Code remote

swyx: task.

Felix: Yes. That’s kind of nice. ‘cause then I can just fire it off. I can go to my next meeting and in Claude Code remote. Now the work is happening.

swyx: Mm-hmm. Yeah. You, you see like you’re already starting to use the cloud over your local machine. And I think this is one of those things where like. Shouldn’t just everything just be cloud first, right?

Felix: Ah, this is such a good group. I’m like solely bad about this. I have so many thoughts about that. Okay. So I generally believe that Silicon Valley overall is undervaluing the local computer. And my default argument for that is always how come we’re all using MacBooks and not like an iPad or a Chromebook?

Um, that there is like still value in, in having a local machine. And now when I think about Clot, it’s this entity that is supposed to be very useful to you, like it tremendously useful to you. I think that entity needs to have access to all the same tools you have access to. Otherwise it’s gonna be hamstrung in like all these complex ways.

And there’s, there’s sort of two approaches we could take. We could say, okay, we’re gonna like one by one chip away at everything that is at your computer and move it into the cloud. That’s, that’s one way to do it. Um, and I think other products have taken that path. I personally, this is a very personal opinion, but I personally, for the amount of tools that I use.

Just don’t have the patience to give another tool like permissions to every single thing and keep those permissions up to date. The second thing that I’m still grappling with, and I don’t have a good answer for anyone just yet, but the second thing I’m still grappling with is what does it look like for someone to slurp up your entire work and put that in the cloud?

Like if I, just as an example, like if you could click a button and it just clone your entire computer into the cloud, is that something that you would want? I’m not totally convinced yet that all everyone will. Mm-hmm. And that is sort of like upstream of all the technical issues we’re gonna have. ‘cause like in general, I think the world is not ready for this kind of stuff.

Like, I’ll give you one quick example that would probably be very easy for us. So as a desktop app, we in theory with your permission, can do a lot of things on your computer, including reading your Chrome cookies. If we really want to do right, we could take your Chrome cookies, you would have to decrypt them for us.

We could put those on the cloud if we really felt like it. Pretty easy solution. That would be super cool. We could just be like, oh, we can do all your tasks in the cloud now. Um, a lot of websites, thanks, include it. If, if they see the same authentication from like two different locations, we’ll just lock down your account and now you have to go to the branch and be like, okay, I, I’m here with my passport.

You actually know that. Wow. Yeah. As tired as well are of the term agent for the age agent future, I think there’s a lot of stuff that sort of slowly needs to catch up and until that’s the case, the way I, as someone’s working on clock and make Cloud most effective is to like put it where you are working.

swyx: Anything else? I thought with our mental model, so like, basically like, uh, part of me also just want, like the more I understand how it works, the more I can use it to its full potential. Right?

Felix: Yeah.

swyx: And so what I’m get hearing from you is you told me to delete the planning thing. You’re not doing anything special on, on the, that’s only exclusive to Qua cowork.

Felix: We have some tricks for this sort of like change week over week. We eval cowork maybe against different use cases than he would evil clock code, right? If you think about it this way. Okay, so like clock code is our eval clock cowork. Yeah. So clock code is like quite optimized for coding tasks and we mostly value it whether or not we’re getting better or worse depending on how good it is at like a typical suite job.

And Clark Cowork on the other hand, we evaluate more against typical knowledge work, the kind of stuff he would find in finance or in like maybe a, like in like a legal office. Um, my personal use case is always like managing my things, like managing my personal mortgage or something like that, right? Or like wealth planning for me and my family.

Those are the kinds of use cases we eval, clock cowork on. And what you might be picking up on is like the subtle changes we make to the system. Prompt what we put in the system, prompt how we steer, clot with the tools we give it. Um, like either it’d be better in one or the other direction and whether there’s a trade off, try us exist a lot.

CLO code will be better of a code and Claude Cowork will be better. For non-coding tasks, will those gaps still exist in the next three generations of models? It’s like a little unclear to me though.

swyx: Yeah,

Felix: because right now these like hyper optimizations we make, I’m not sure for how long they’re still be relevant.

swyx: I think what I was referring to was also, it, it just, uh, it qualitatively felt different when I probably, it’s just all prompting and I’m reading too much into it, but like the, the fact that it comes out with like a nine step plan, I can edit the plan and give feedback and, and, and see it execute the plan.

Yeah. It felt more long range than in Claude Code, but maybe that already existed in Claude Code and you just build a nicer UI for it.

Felix: It’s kind of both. Um, like if the Clark Code people who build the planning functionalities would city, they probably say yes, we have all of those things in Clark code and they do.

Um, I think people tend to give cowork. Tasks that are maybe of longer time horizon, I thought is

swyx: so long. Yeah.

Felix: That’s like one thing, right? It’s just like that the, the chunk of work tends to be maybe a little bigger. And then the second thing is that because the work, when it gets longer, it gets a little bit more ambiguous.

We do tell co-work to make heavy use of the planning tool or to make heavy use of the ask user question tool, right? We do want it to come up with like. Different scenarios of, okay, tease out what the user actually wants. Don’t go off to work for like four hours and then come back with the wrong thing.

And you’re probably picking up on that.

swyx: Yeah.

Felix: Um, I wish I could tell you I like built this magical thing and it’s like, there’s some secret sauce,

swyx: but No, no, no. I mean, it’s, it’s just clarity is good that, you know, engineers just want to know. Yeah. They can, they can plan around it. And then I think also for me, um, I am realizing I have to switch to my, my other machine because this is a new machine that doesn’t have my session.

But, uh, yeah, the, the, the planning is really important for, for me to like approve or like to see whether it’s like, it’s right. The ask is, the question is so beautifully presented. I mean, it also, it also available in like cursor and, and in Claude Code. But like, I, I think like it’s so nice to see that it, like it’s kind of for me like to understand that it gets me, it gets what I want to do.

Felix: Yeah.

swyx: Yeah.

Felix: It probably very hard

swyx: just on the topical evals. Mm-hmm. When you say eval, I think people are very vague about what it means. Is it just like vibe testing or do you have like automated programmatic evals of Claude Cowork?

Felix: When we say eval, uh, what we really mean is that we essentially take the entire transcript, including all the tools that clot has available ultimately to it, and we then measure what are the outputs, depending on what we tweak, right?

So we do run that a lot. We use that in training. Um, we use that in, in like, if you sort of separate out post training from like the scaffolding around it. Cowork sort of exists in the scaffolding space, but obviously we also train on it a little bit. Um, so when we say eval, we mean given the certain transcript, what do the outputs look like?

Including the file outputs as well as like the actual token outputs, like the ones that you see in the chat window.

Alessio: I’m curious, um, how much of the failure modes are the model intelligence versus like the usage of the end tool to put the intelligence in? Like the well planning is like a good example, right?

It’s like one thing is to come up with a plan. The other thing is like make a nice spreadsheet. Yeah. That kind of runs you through the plan. Like how have you seen that? Well,

Felix: the thing that I grapple with a lot is that whatever scaffolding you come up with, I think we still have a bit of sort of like model overhang where the model is dramatically more capable than right.

Users end up using it for. And I think part of that is that we’re just not getting the model all the tools to do all the things that’s theory capable of, right? There’s like one thing, um, however, whenever you do build the scaffolding, I’m sort of wondering at what point, at what point will that scaffolding go away and like how much you invest in figuring out what the right scaffolding is.

It’s kind of up to, it’s a little bit of a bet. And one thing that I as an NJ quite enjoy is that like working in philanthropic and working at a frontier lab, I maybe have a little bit more insight into what’s coming, coming down the chute in terms of like, what’s the next model, what is the model capable of?

What is good at, what is it bad at? And I’m, I’m increasingly wondering, is the right thing for us to like really invest too much in sort of these like scaffolding corrections where the model might otherwise not misbehave, but just not do the thing that you want?

Alessio: Yeah.

Felix: Or is it to just like give it as many capabilities as possible, try to make those safe so there’s the worst case scenarios, likeno status might be otherwise.

And then just simply wait a second for the next model drop. I’m personally, currently more leaning into the ladder. I think we’re gonna see a lot of like applications and companies that do very impressive things with ai that in the short term might seem very effective ‘cause they’re very specialized to individual use cases.

But I think once models get better generalization and get better at like those specific use cases without being super guided on those, I’m not sure how long that’s gonna stick around. And you can kind of, kind of already see this in like skills and NCP servers, right? Mm-hmm. We’ve, we’ve already seen sort of this like slow shift from MCP service to skills.

And like, maybe a good example is Barry who made skills. He was initially hacking on something that honestly looked a lot, looked, looked a lot like what Cowork does today. It was sort of thinking about what if cowork, but for like people who don’t wanna build code. Mm-hmm. And, um, he too did that as a prototype inside the desktop app.

One of the first use cases we thought of were, okay, what, what are like coding like use cases that could really benefit from graphical interfaces and like from being a little separated from the actual underlying code. And everyone comes with the same answers. Data analysis,

Alessio: right?

Felix: Yeah. Or saying how many users do we have today?

How many, like, it’s always data analysis. And I think the thing that ultimately led to skills is that we wanted to connect this little prototype to our data warehouse and. The team very quickly discovered that like instead of building a custom tool for the thing to talk our data warehouse, they just like meet and embarked on follow like mm-hmm.

Dear Claude, if you want to get data, here’s the end point. Here’s what the API looks like. You’ll figure it out.

swyx: Ah.

Felix: And then it be hand over control. Yeah, yeah. Also just like maybe go one step up in the layer of abstractions, right. Just, yeah. Instead of, instead of telling the thing, here’s ACL I, please call the CLI, or here’s an MCP.

Please call this ECT shape. Just like this is the end point. If you wanna know something, if you post here, maybe you can do post sql. It’s gonna be okay. And that ended up being so effective that they started trying the same pattern of like just giving the model a markdown file that describes whatever it needs to do.

That the whole thing eventually became skills and we’re like. We should package this up. This is a good idea.

swyx: Yeah. Um, we’ve had Barry Mahesh, uh, on, on our conference and uh, he’s uh, definitely got a good idea there.

Felix: Yeah.

swyx: I wanted to show you the, how I’ve been using Claude Cowork.

Felix: Uh, this is was my favorite part.

swyx: This is this. So this is like me, uh, this is how we run the Discord. Uh, we literally, uh, at first I didn’t trust Cloud Core. This was my very first usage.

Felix: Okay.

swyx: Right. So then I was like, okay, I will just try to manually download from Zoom all my recordings and upload it to YouTube. Yeah. Because this is a very laborious process.

I got a click, click, click YouTube, um, isn’t super user friendly. Uh, and it just did it. And then I was like, actually, you know, even the download from Zoom part, I should also. Put into Claude Cowork, and then I did it right. Here’s a bunch of, and it starts compacting here, and it, and it, it starts to even be able to do things like look through the individual frames of the video to name the video so I can upload it auto automatically.

Oh, that is, and this replaces my job as a YouTuber. We will forever appreciate your creative Yes. You know, and so that’s great. Uh, but then by the way, it compacts and makes, makes like a new thing, right? So I, I don’t, I don’t have the initial, initial thing, but then I asked it to make its own skills so that it, so that something that’s repetitive and one-off and human guided becomes more automated and I can use the skills independently and reuse them.

Uh, and it obviously you can write skills and that goes into context and skills at the bottom here, which is, which is so nice. Um, so I have all these skills that, that I now sort of do on a weekly basis. Uh, I know you’ve released scheduled Coworks, which I haven’t done yet, but

Felix: course I should try them. I, I think this is like so wonderful and fun for me to see because.

One thing that is very fun for me about skills in particular is that they’re so easy to make. Like anyone can make a skill, like a text message, could be a skill, and they can be so hyper personalized to you. And this is like sort of the subtraction layer, right? Like, um, I, I’m just guessing, but I assume, heck, you are very good at your job.

You’re probably given this thing some guidance about how to do it, right? I,

swyx: I just said, wrap everything up into, into a skill, right?

Felix: Yeah.

swyx: And then, uh, and then I was like, actually, sometimes I might need to break, uh, things apart because some parts fail or some parts might be needed in individually. So I told it to split one skill into three skills.

So it’s like a skill splitting thing, and then there’s like a parent skill that just orchestrates all of them if I want to use that. You know, like, um, I think that’s, that’s like really good. Uh, and, and, uh, there’s, there’s one more part, which is the, uh, Google Chrome thing that I told you about.

Felix: Yeah.

swyx: Where I’m like, okay, you know, what’s better than uploading, using Claude Coworks to YouTube?

Like actually. Looking at the docs to like programmatically upload to YouTube and then putting that in a skill. And I’ve never done that before. I don’t want to deal with Google Cloud. Yeah. So Claude Cowork does it for me.

Felix: That is really cool.

swyx: So, so I, I just, I don’t care. I just, like, I do a thing. I don’t, it doesn’t really matter.

Felix: That is really cool. And then you’ve, I assume paired the skill just with the script that it’s built.

swyx: Yeah, no, I just update, update the skills.

Felix: Oh, that is beautiful. Yeah. That’s wonderful.

swyx: It’s kind of like a skill, like, uh, uh, basically I think like the way that people ease into Claude Cowork is like take a knowledge work task that you would normally be clicking around for and then, uh, try to turn, turn that, and then you do the, okay, well what if you went further?

Okay. And then when, if you went further, when, if you, and it sort of expand the scope of cowork as you gain trust with it and, and also teach it how to replace you.

Felix: Yeah. It’s like a little bit like playing factorial, but for your own life. Uh, like you say, you start really small.

swyx: Yeah.

Felix: You start automating something really tiny and like.

Once it clicks, you keep adding onto this like automation empire. Just like make your life easier and easier. My favorite skill has been, um, every single morning Kohlberg starts looking at my calendar and make sure that there’s conflicts because people tend to schedule a lot of meetings, sometimes last minute, sometimes miss it soft and painful.

And a lot of products have existed like that A lot. I’ve written in the custom prompt there. I haven’t made it a skill, um, honestly should.

swyx: Yeah.

Felix: But I’ve given it like pretty clear instructions about okay, here are some people, if they book over other meetings, I’m probably gonna go to their meeting. Like if Dario schedules a meeting.

swyx: Right.

Felix: Not try to reschedule down. Right. Um, and I think there’s some other rules in there about like what kind of meetings I care more about what kind of meetings I care less about. What is okay to like, maybe pun like when I want to be, when I want to be working, when I don’t want to be working. And it’s those really small things that I can think kind of click with people.

Right. When we launch co-work, I think one of the US races that went most viral on Twitter. X was clean up your desktop, which is stuff, because silly, that’s such a smart thing, right? Like you don’t need to model to clean up your desktop. Not really. Um,

swyx: like this, like clean up my desktop.

Felix: Yeah, exactly. Yeah.

swyx: I need to, I need to choose my desktop, right? I guess give it access to my desktop.

Felix: Yeah.

swyx: Okay. Uh, okay. This is very scary. Oh, we’ll do it.

Alessio: I did, I did it with my downloads folder. It was like, you have so many term sheets and there’s like eight copies of your rental lease for your office. I was like, all right.

Like, don’t yell at me.

Felix: It’s like, it’s not such a small task. And then like, I, I would never go out there and normally otherwise and tell people I’ve pulled a product. It can organize your folder. Right. Um, because it feels small. But I think to your point like,

swyx: oh, here’s, here’s the, here’s the ask user questions.

Felix: Yeah.

swyx: Uh,

Felix: beautiful. Right. Elite obvious junk. You probably shouldn’t click that.

Alessio: No.

Felix: If he’s not done right.

swyx: As long as it’s reversible, I don’t

Alessio: make up blend to,

swyx: yeah. Uh, yeah. No, I, I have a, I have a typical, everything is super messy folder. So, yes. I think this, this is super helpful. So this is a pretty simple task.

Mm-hmm. But I’ve, okay, here it is. Right. Here’s the progress. I don’t see this in, that’s why I’m like, this gotta be something different than, uh, than Claude Code, because I’m like, we

Felix: do. Yeah. That’s, we do system prompt that. We’re like, all right. We want you to think about like, this task Yeah. Methodology.

Yeah.

swyx: And then I can, I can, I can do like little suggestions for, for, for these things. It’s beautiful. Look at this. I, I can, I can like say like, oh, don’t do that. Don’t do this. It’s amazing.

Felix: I’m so happy. You like it. Um, I mean, the other way around, like we’re part of the Clark core team, if you would like this in Clark COVID.

swyx: Yeah. Yeah. Yeah. Uh, so, so yeah, I mean, uh, this is really good. Obviously I, I’m like kind of raving about it. Uh, you know, I have other things like sign up for pg e so if you can do phone calls for me, that’d be great. Um, I, I do, people

Felix: have done that. Obviously you can’t do that natively, but people have done that with like, various other providers.

swyx: Yeah. Uh, and then this is like signing up for the Figma MCP. Um, I, I really am trying to do like everything, um, data analysis as well. I do think, um, oh, design to code, uh, very, very good. Right? So like, here’s a Figma file, take it. And then this is where like a lot of other tasks is like knowledge work, like replace my manual clicking, but this is no, I would normally use Claude Code or uh, Claude Code for this, but because I perceive that you have better Chrome integration

Felix: mm-hmm.

swyx: I, I think you can actually do a better job of this. And I, this, this is one shot at my, uh, conference website.

Felix: That’s pretty cool. Like at some point I would love to like, hear how you feel about code. In the desktop apps, which is like I never use, which is the, the same team. Same team.

swyx: So I use the call code in terminal, which I, I perceive to be the default way of cloud coding.

Felix: So one thing this has,

swyx: sorry, I’m just like, I’m not

Felix: here, I’m not here. All products. Can I talk about other stuff? Like I, I’m not sure if people out there wanna like hear me advertise my stuff for like an hour. Please do that. Um, this thing is like a builtin browser, which is a thing a lot of products have said.

Yeah, it’s a builtin browser. And I think giving cloud eyes into like what you’re actually working on makes it so much more effective. And that’s probably what you’ve seen in cohort because it can see Chrome, it can like debug the dom, it can like see things. Um, that does make it more powerful.

swyx: Yeah. So, so I think, uh, my mental model was kind broken.

‘cause I only use this cowork because I thought it had a, a browser thing in it. But I understand that the Claude Code app. The app version of Claude Code does have a built-in browser. I’ve seen, I’ve seen this preview thing.

Felix: Yeah.

swyx: I just, I’ve never used it.

Felix: But in the end, in the end, you sort of have it by hard.

Yeah. You basically get the same thing. Right? Like the, the, the additional skill that you’re describing is chart is better if we can see what it’s working on. Right. That’s, that’s sort of like the summary here and like whether it’s using your Chrome

swyx: Yeah.

Felix: Or it’s just like making up its own little like browser.

It doesn’t really make a big difference because either way it’s gonna see what it’s working on and that just makes it much better. And then you don’t have to run QA for your cloud.

swyx: Why doesn’t it pick up my existing Claude Code sessions? ‘cause I, I mean, obviously I’ve used Claude Code, but Excellent question.

Um, don’t have a good answer other than like, we’re honest. Just haven’t Yeah. This is what the Open AI team does. Okay. Uh, cool. I I I don’t have other, like, I, I just, I, I do wanna expand people’s minds and also maybe show people if they haven’t really done it, but like, I, I think it’s very interesting how I sometimes use this more than I use, I mean, I use dia, right?

Yeah. Um, I, and I use, uh, I’ve used like all the other agentic browsers and philanthropic didn’t have to build an agentic browser because you just had Claude Cowork and that’s enough.

Felix: Yeah. I also think like maybe integrating with number of excellent browsers out there, it’s like currently on my personal priority list, a little higher than like trying to rebuild a browser from scratch.

Yeah. You know, never say never, but I think going back to this idea of like, we wanna plug this into an entire existing workflow, I think our goal is actually to not replace any of the applications we have in your computer. But instead of like, work really well within a new workflow,

Alessio: make the new one. Yeah.

Are, it seems that nowadays, especially on the browser, most of the innovation is like user ergonomics. It’s not really like the underlying browser engine. So I feel like to call it, it doesn’t really matter if it’s like the, uh, or Chrome or Alice, whatever.

Felix: Yeah. We wanna, we wanna meet you wherever you are.

Which is like, like obviously I would say that, but it’s also just generally true because I don’t wanna shrink my potential user base artificially by saying, okay, like, I’m gonna start building for the people who are willing to switch browsers.

Alessio: Right.

Felix: That’s such a, like, you know, like many lawsuits have been filed over who gets to review the browser and like a lot of money has switched hands over the question of like, which browser is default and which search engine is default within the browser.

Um, I just wanna build for, yeah, I wanna build for swyx essentially. Like, I wanna, I wanna, I wanna build for people who have a number of annoying tasks that they feel like. Maybe clock could do it. Could do it for them.

Alessio: Yeah. What do you think about skills portability? I think there’s been one thing, I use another thing called zo, which is kinda like a cloud computer plus agent.

And I have a skill to add visitors to the office. Yeah. So whenever somebody has to come in after hours, they need to check in downstairs. Um, but I wanna like text the thing, so it doesn’t really work in, in cowork, but now that skill is in the zone harness and it’s not in my cowork thing. And then if I make a change, it’s gotta, I gotta sync them.

How do you see that going? Like I see memory as like. Cloud personal, kinda like, I don’t necessarily want my memories to be cross thing.

Felix: Yeah.

Alessio: But I do want my skills to be cross agent that I use. I think with MTPs, people do the same thing. It’s like, oh, Mt. P Gateway. Mt P registry. I don’t really know if that’s like a business.

So I’m curious like if you’ve had any thoughts in the area.

Felix: I think for me, this is sort of where I go back to the really basic primitives for our skills are file-based instead of like this complicated thing that exists inside a place somewhere that is like super proprietary. I’m really leaning into the idea of like, it’s all just files and vultures, and that makes it very portable on its own.

Right. We do have skills as part of this container format, which was just called plugins.

Alessio: Mm-hmm.

Felix: And plugins are available both for Claude Code and Claude Code work the same format, and you can install plugins. This works in cowork today. You can basically say, I’m gonna add a whole, like just a GitHub repo as a.

Skills marketplace or like a plugin marketplace. And that’s how we’re doing portability. I think we have a lot of room left to grow in. How do we make it easy for people to know that they can write skills? How do we make it easy for them to just like, share a skill with you? Because obviously all the words I just said, right?

Like I’m losing most of the knowledge worker base out there, right. And start by saying, oh, you can connect to GitHub repo. It’s not exactly how most people will end up working in like a general knowledge worker space. Um, but I think there’s something there. And another thing that’s there that I think has not really been properly explored is the, the, the combination of which part of the skill is very portable and then which part of the skill is like very personal to you.

Right. And I think that’s something we haven’t really solved as an industry. Hmm.

swyx: It’s like, which, how you wanna introduce more structure to the skill or have always have like. Public skill, private skill, you know, pair. Yeah, yeah. Kind of. I think there’s

Felix: like a, like the easiest way to do this, which is we do like use string interpolation or something.

Right, right. Yeah, yeah. Insert username here, insert like phone number, insert, like known folder, locations, that kind of stuff. Um, that’s probably clunky. That’s why we haven’t built it. Um, but I do think someone is going to come up with like an interesting way to keep everything we like about skills. The portability is just a file, it’s just marked down.

It’s just text, honestly. Right. Like a text file words. The complete lack of structure, which means you don’t need any kind of tutorial to write a skill. Just like explain it to Claude the way he would explain it to me and Claude will probably get it before I work. Mm-hmm. Right? You’re just like, for booking a flight, tell Claude how to book a flight the same way we tell him somewhere.

I just started working here today. But combine that with a very like, personal thing. Um, maybe we’ll stick with a booking a flight example. I don’t actually think. AI should be booking flights. I think the tools we have is yes.

swyx: Yeah. Finally, somebody says it. It’s the default demo that everyone’s making.

Felix: I’m

swyx: like, I even against like booking demos, it is not a good showcase.

Felix: Yeah. I’m like, I just wanna book my flight myself. But, um, I think there’s a lot of things that have a personal and a non-personal component and that’s maybe why people reach for flight booking because some things are very universal. Yeah. Super flight is usually better, right? Like few people try to book the most expensive flight.

And then some things are quite personal about like what times you prefer, which seat you prefer, which airports you prefer. Combining that and like a skill format that is actually portable, compatible, easy to understand for people. I think that would be very exciting. We just haven’t figured it out yet.

Alessio: Yeah, I think the text part every, I think everybody by now has some sort of like cloud file thing. Either Dropbox, Google Drive, whatever. So it feels like in a way it should basically like sim link. My skills into all my agent harnesses. Yeah. Just keep those ing like we have internally this like valuable tokens repo, which is like all the commands sub agents.

It’s good. Uh, and then I build like a TUI where you can start it and be like, you know, install this command and this three sub agents into this agent in this folder and just copy paste this. It doesn’t do anything. It literally cp the file into that. But I feel like there should be something similar where like whenever I go into a new thing, it’s like, hey, here’s like the link to exactly the cloud folder and just bring down these skills into this.

Yeah. Like today it doesn’t quite work like that. Like if I install a new agent, I cannot, I have to like copy paste all the skills and I don’t even know where they are.

Felix: Yeah.

Alessio: That’s like the big problem. It’s like where do I find them?

Felix: Yeah.

Alessio: Um, so I’m curious like in the future like that, that almost feels like my personal productivity thing will be my skills.

Felix: Yeah.

Alessio: Is not really the product that I use. Everybody has access to the same product. But today there’s, that just looks like copy pasting ME files, I

Felix: think so many things I, I really like thinking about agents and LLMs just as like another coworker. So many attempts have made to build documentation companies that are like, oh, we’re gonna solve oil documentation problems.

Um, I myself, like spend a little bit of time working in notion, right? I’m like deeply familiar with the concept of let’s get everyone on the same page. Mm-hmm. Right? And what you’re basically saying here is you want all your agents to be on the same page about your preferences, about the skills, about the way they ought to work and like how they ought to execute.

And I’m not sure what the right thing is going to be if it’s going to be some, some company that can say, all right, we’re as an independent body, we’re not trying to like, push into any particular product. It’s our job to be like the skill authority, and we provide, I don’t know, we’re gonna be the Dropbox of skills and we can just sim link us into all the products we want to use.

I’m not sure that’s gonna be viable business, but as, as an idea, it would be cool.

Alessio: Yeah. Yeah. I think so many things are just going away as businesses. It’s like, how am I supposed to do it? I’m not even asking somebody to make a product about it. Like yeah. I wanna personally know. And there’s things like you said, it’s like you almost wanna skill and then interpolate it between personal and work.

So if I’m booking a fly for work, it’s different than I’m booking a flight personally.

Felix: Yeah.

Alessio: In some ways, yeah. But like a lot of the scaffolding is the same, you know? Cool.

Felix: I mean, as an engineer I will tell you like, you know, technic a person to technic a person. I will just be like siblings.

Alessio: Well that’s what, that’s what I do.

We call that MD and agents that MD’s just the same how sim length. And so it is like, that works, but it feels like, yeah, I don’t know. Maybe

Felix: you can always go one, you can always tell cowork problem and then cowork will solve it for you. Just make the siblings. That’s like one way to do it.

Alessio: That’s true.

That’s true. All right. Everything is called cowork.

Felix: Uh, potentially spicy. Question for both of you.

swyx: Uh, which of these industries will go away?

Alessio: Okay, so what Felix was saying before is interesting. There’s busy like. The short term pressure of like, we need to turn these tokens into valuable things, which is I should build the last mile product that harness the model.

And then there’s the question of like, long term, which ones are gonna still be valuable? And I think you’re kind of seeing this today with like, uh, you know, the coding space in a way is kind of like everybody’s moving up and up in stack because you need more than just turning tokens into code. I think search, like enterprise search is kind of saying the same thing.

Like with G Clean and like all these different companies is like, at the end of the day, if Cowork is the one doing all the work, the search itself is like such a small part that like, I don’t know if I’m really gonna pay that much money just to do search. It’s almost like everything is like a cowork vertical.

So like how much can cowork first party support?

swyx: Mm-hmm.

Alessio: And how much can it not? I think for a lot of these things, the planning thing that you were showing do Which one? The planning. The planning.

swyx: Okay. Yeah. Yeah.

Alessio: That’s one thing where like most of the value that these agents provide is like they’re better at planning for specific tasks.

Yeah. And have better tools for it.

swyx: Yeah.

Alessio: But I think the models are now moving in that direction and they have the right harnesses and they’re on your computer. So for me it’s almost like if for the end customer trusts your startup to be the provider of that task result, then I think that works. This is, uh, something that, this is a short

swyx: spike that we’re, we’re working on.

Uh, yeah.

Felix: I think, look, I’ll, I’ll, I’ll tell you this, like I don’t think I’m the best person to like actually estimate which industry is going to be hit the hardest. But I do think that at philanthropic as a group of people, we’re deeply worried about the impact. That the tools are going to have on the labor market, especially for like junior employees that, because I think, I think it’s only honest to say that when we talk about automating a lot away, a lot of the work that we personally find annoying that we maybe think’s not the best use of our time.

In a lot of industries, that kind of work would’ve been given to a junior entry level employee. Yeah. Right. And I think it’s, it’s only, it’s only right to be really worried about that and like worry what that’s going to do in particular to people like enter the shop market.

Alessio: Mm-hmm. I have a solution for that.

Which you make them, you create simulative jobs for them.

Felix: Okay.

Alessio: So this is, this is like half joke, half true. So if you think about software engineering, when you’re like a junior engineer, you work like 1, 2, 3 years. And in those three years there’s like maybe like a handful of moments where like you really learn something.

And then a bunch of other days where like you’re not really progressing.

Felix: Yeah.

Alessio: I think now we can use AI and these models to actually like shortcut these careers and almost like simulate the early years of your work and like just make them like super dense and like these learnings, it’s like, hey, we’re working on this feature, which is like a distributed system and you need to learn this thing that might take three months at a company.

And so you take three months here, it’s like we’re just simulating the whole thing. It’s actually not a real thing. And in one week we kind of speed run through the whole thing and you kind of learn your lesson from there. And we kind of repeat that in like one year. You basically get like three years worth of like projects and experience.

Yeah. I think it’s harder for like things like sales or for things like, you know, marketing because you don’t really have a way to get the feedback loop. But I think a lot of it, it sounds kind of silly, it’s like you’re making the new effect job, but it’s almost like you go to college, right? People pay to learn how to do it, and this might feel similar where it’s like, hey, we have the.

Jane Street Simulator is like, you wanna come work at Jane Street? We’ll just put you in the simulator for like three months.

Felix: Wow.

Alessio: And you’ll come out of it. It’s like, you know, I’m ready.

Felix: So there, there is an aspect here. I’m not an expert enough to like actually know what, what is going to happen to marketing or legal or finance, right?

Like, I don’t work in those jobs and I, I don’t think I should talk about them, but I am an engineer and I think I have a pretty good idea of what engineering is like. And I think one thing we’re sort of seeing is that as a company and also as, as the public, we’re like deeply worried about entry level, but we’re also seeing more senior engineers accelerate it.

If like they’re more productive. They, they actually increase the value they provide. And the thing that I’m thinking about a lot is the fact that even before all of this happened, um, I’ve always had a lot of respect for the University of Waterloo and the, the new grads that have joined my teams as from coming from the University of Waterloo always felt like.

More ready than new grads will like literally spend their entire time at the university regardless of how good, but never actually had to work inside an environment where you have to ship things that eventually will be used by users. And I’m, I’m, I’m German. I like initially went to German University and I think the, the, the like information systems programs, there tend to be very theoretical, right?

Like I often give people the example of like trying to become a doctor, but you first have to do four years of biology and as a result when you get a new grad, you sort of have to teach them what it’s like to actually build products and to work in a company and like work with other people. And like some people will have different opinion and like, how do you do all of those things?

And the University of Ulu, it seems like they just. Spend half of their time. I dunno if it’s true, but I think it’s, it’s a year, right? They spend so much time,

swyx: part of your job, uh, a cu a curriculum to do spend a year in internships.

Felix: Yeah. They just like go from company to company. They show up on your team as like a junior engineer who spend like 20 companies.

Not really, but like, it seems like a lot of my new grads have also briefly worked at Apple, Google, Tesla. Yes. And uh, there’s a common meme where they like collect all these logos, like infinity stones, but, and they always put it on LinkedIn and it is very unclear that they’re an intern. Like Yeah, yeah, exactly.

But it does actually make them so much better compared to other new grads. And I wonder if that’s a useful model maybe for the future when we also have to like, crunch down the amount of time you have as a junior employee. ‘cause the value you have as a junior employee is going to like, be impacted.

swyx: My sort of pro young people take is that they’re, you’re more, uh, you have higher neuroplasticity, you can learn more, you have less preexisting biases.

And, uh, what I is assuming is true for you, what OpenAI often says is that. Actually it’s the, the younger, like fresh grad engineers that use Codex or their coding stuff, uh, more innovatively than the, uh, experienced engineers who have a set and preferred way of doing things.

Felix: Yeah. As I talk to people, I, I someone experience.

swyx: Yeah. So maybe you’re more AI native. Yeah. And therefore you’re, you, you get cut. But like, I think the problem is you don’t need that many of them.

Felix: I mean, philanthropic is on the record as saying we do believe that the impact on the market is going to be sizable and we do not think that people overall are ready.

Right. And we do actually think we should probably talk about it as a society much more. Yeah. I’m not sure that I’m like the individual that can add like anything useful there. But I think as societies with economists and, and governments that need to wrestle those questions in a way that is probably more meaningful than me wrestling with them, we’re probably not doing good enough.

swyx: Well, we, we’ll try to educate and then I think also just releasing frequently as, as, as you guys do, or probably maybe too frequently

Felix: Yeah.

swyx: Uh, is helping people to adjust over time. Right. Rather than one big bang thing. There’s like sort of this gradual takeoff that people are living through that we

Felix: Yeah.

swyx: Waking people up. Right.

Felix: Yeah. And I, but I think a lot of us like wondering at what point do we actually have full takeoff, right? Like at what point is there, we’re all sort of expecting this like big bang moment where things will accelerate so quickly that it becomes a self-reinforcing loop.

swyx: Mm-hmm.

Felix: And at that point, it’s sort of like off to the races and there will be no more like slowly catching up.

You notice just have cloud being so good at everything.

swyx: Yeah. It’s when cowork is training models, it’s when it’s looking at tensor board and Exactly. Weight and biases and training things.

Felix: I like we can all debate like how many years it’s away, right? Like some people make a better route, like maybe it’s 10 years away, maybe it’s a year away.

Um, I’m not entirely sure where, where I come on this time, but I’m not totally sure that ultimately it matters all that much, whether or not it happens in four or five years. If we have a decent one, certainly that’s going to happen. It’s probably something we should wrestle with.

swyx: I wanted to talk, so by the way, the, the scheduled task complete, uh, the, the, there’s the clean my desktop task complete and it did it organized by file type, which, okay.

But, you know, I was trying to get it to do more sort of thematic, like read the file, understand what it’s about, group by, uh, the, the topic rather than the file type. But

Felix: I mean, you can just follow up and have it do that. Oh yeah. Here, like it did, it is proposing That’s right.

swyx: Yeah. So it’s, it’s got some like topical things, but uh, yeah, I could probably do better.

Like, yeah, so like I probably need to give it a skill to read video files so that it understands here’s how I like to,

Felix: honestly though, like, um, I see that you’re using Opus 4.6, right? Like my recommendation for people is increasingly don’t worry about it anymore. Just like tell it what you want it to do.

swyx: Yeah.

Felix: And it’s probably gonna figure out a way to do it. It might not be the way that you like necessarily or the way that you’ve gone about it.

swyx: Videos, deeper,

Alessio: lower outsourcing, organizing all of this. So let’s fight. Yeah. Yeah.

Felix: I’m honestly like, so curious what cloud is gonna come up with.

swyx: I’ll kick that off.

I wanted to also just talk about the, the overall, uh, you know, you talk about data analysis, you talk about like, uh, your, your personal finances. You also said, uh, which by the way for us is very timely tax season, right? Like Yeah. Use cloud core for tax season. It is not responsible for any mistakes, but might as well, right?

Like it’s, it’s free knowledge work for you. Yeah. Uh, so I just like, I think cloud for finance is a big deal. Um, and this is definitely like in that mix. I wonder, is it like, do you, is it a separate team? Do you talk to them? How important is it? Right. Like, because you can also natively output Excel files now.

Felix: Yeah.

swyx: Just

Felix: talk about the

swyx: finance effort

Felix: grow. Yeah. We care about the verticals quite a bit. So we do have a dedicated verticals team. We have a dedicated enterprise team,

swyx: and those is business engineering, not sales.

Felix: It’s engineering. Yeah, yeah, yeah. It’s engineering. So we do have people who sort of come to work every single day and they, they ask themselves, how do we make co-work extremely effective for people in those specific industries?

How do we make it easier for them to understand, how do we make it easier for them to plug into this and like sort of get the same value out of it that software engineers get? I think it’s no real surprise that software engineers ended up being sort of at the forefront of the entire AI moment because so much of it is this like Rub Goldberg machine nest where like we’re already used to automating things, right?

Like it’s part of our job. Yeah. So we care about it quite a bit. I think it also like really matches what we see. Cloud being very good and as a model, I think it provides tremendous amount of value to those customers in particular because. We can do so much with the amount of data they have. Those are like data heavy industries.

Their industries for correctness matters quite a bit.

swyx: So for us of, I’ve used it to analyze my business, I just can’t show it. So

Felix: it’s two sense. I had a similar question about, about taxes. Like, I did tweet, I did tweet about the fact, I did tweet about, oh, COVID is doing my taxes. This is honestly incredible.

And, um, it’s like annoying. He is like, this is so cool, but I’m not gonna, Twitter is maybe not the audience that needs to like see my tax return.

swyx: Yeah. That way. Here, here it is. It’s it’s reading on the videos, so it’s like Yeah, it’s getting more, yeah.

Felix: How did it actually do it? I’m actually curious.

swyx: Oh, usually it just like, takes a screenshot and then it reads the screenshot vi by vision.

So this is what I do for my, my Zoom upload thing, right? Because I, I have paper club sessions that I need to upload to Zoom and I want it to automatically. Uh, title them and do show notes and everything. So it just take screenshots and try to try its best. Yeah. It wouldn’t probably benefit from transcribing, which it’s doing by, it’s operating by Pure Vision now, but it’s good enough.

Felix: Yeah.

swyx: And then I, uh, I do have to call, uh, out to Nano Banana to do images. So unless you guys do images for me, uh, I have to call other people your images.

Felix: We’re aware. We’re aware. It’s, it’s just like so fun for me because like, this is the thing that I’m increasingly doing, like increasingly curious about cloud’s, creativity and like figuring out what is great Claude’s approach is like some problem.

swyx: Yeah. Vision for everything is, is like the, the superpower, right? Like, you know, and computer use, you guys were the first to do computer use, right. And when it was launched, I was very unimpressed. I was like, it’s slow, it’s unreliable, it’s wild. How much better? ‘cause it is one year ago.

Felix: Yeah, I know. Like it was barely usable.

Yeah. I, I remember it was very usable, but is it wild how much better things have gotten? Yeah.

swyx: Yeah.

Felix: Over that one year

swyx: we went to the anthropic office because you, uh, for the launch event for computer use. Like there was like this hackathon. Yeah. And like nobody hack on computer use.

Felix: But I did see, I, I I don’t know if you’re okay with me saying that, but I did see briefly that you do have like a, like an automate Mac, SMCB server installed.

Right. Uhhuh, you use that ever.

swyx: What? Sorry? Which one? Where?

Felix: Um, if you go to your settings.

swyx: Oh, settings. Okay. Uh, where, sorry, this one?

Felix: Yeah.

swyx: Yeah.

Felix: Um, I noticed that in your connectors,

swyx: Uhhuh. Uh, I probably said it at one time, but I don’t use it actively.

Felix: Oh, okay. The

swyx: a max automated. Yeah. Yeah. So, so I, yeah, this one I really wanted to like, just automate everything in my thing.

I didn’t find, I didn’t find it super reliable.

Felix: Okay.

swyx: Why?

Felix: No, no, no question at all.

swyx: Cloud is much better writing Apple Script and executing its own Apple Script than relying on these, uh, third party tools.

Felix: Yeah.

swyx: Uh, so I’ve increased, I, I initially installed Im CP and like all these other fcps that people built, and, but now I don’t use any of them anymore.

Like just, just let cloud write its own thing.

Felix: Yeah. It’s

swyx: gonna be more custom made. We keep going up the stack,

Felix: but if using computer uses like a fairly interesting area to me, and it’s like also interesting in the sense that I don’t think we’re far away from, I don’t think we’re far away from clapping, very effective, but like using your computer and not just it’s theoretical computer.

Alessio: Mm-hmm. What’s the relationship between the user and the computer? Like, uh, there, there were some tweets about how huge some of the VMs, the Claude Cowork creates ours, like 12, 15 gigabytes and people complain. Yeah. But at some point it’s like, if you’re using the computer, you’re taking action on, it’s, it’s just your computer.

And I’m just looking at it, you know, it’s like, I, I think that’s why people like the idea of like the Mac mini and the open claw or whatever on it because it’s like, it got its own home. You know? It is doing its thing, I’m doing my thing. I think there’s some kind of like, not like risk condition, but it’s like, okay, if I kickstart this task now I can’t really use the computer.

Felix: Yeah.

Alessio: You know, because car coworkers doing things on it and it’s kind of awkward, like, yeah. I’m not sure.

Felix: I, I do think it’s a super interesting area because I, I can maybe tell you like some of the things I thought about that I think are actually a bad idea. So when, when we initially started working on cowork, I, I did have some dreams about, well, would it look like for cloud of its own cursor?

Could be cool, right? Like it’s a computer, we can write code, we can touch everything. Like who says that computers need to have one cursor? We could do a second cursor, but that actually breaks down quite a bit. Even if you go and like present cool dreams to both Apple and Microsoft, you’re like, wouldn’t it be cool if, um, it breaks down quite a bit?

‘cause so many of our models on a computer are built around this idea of like, there’s only one thing working on it. Yeah, there’s like a foreground app, a background app, cloud and Chrome can work in the background, but that’s like within one application. But the operating system layer, that is a lot harder to implement.

So I’m, I’m still grappling with what, what does it mean for cloud to actually act on your computer. It’s the right format for cloud to have its own computer that you set up. And maybe every now and then you like zoom in and you play with it. Or is the right format for Claude to just like, wait until you are.

Stepping away for a little bit and take over while you’re gone. Or it’s the right move for cloud. Just like if it’s on computer in the cloud, and like whatever you want cloud to do, you have to set up yourself. Right. There’s like a, there’s like a number of different options. Um, this is the thing I think about a lot, like what is the relationship between you and your computer and you and your data on their computer?

Because how intimate that relationship is kind of depends on the tool and Right. The thing that you’re current looking at, right? Like we’re quite comfortable sharing some things, very uncomfortable, sharing other things. And I think whatever product is gonna be successful, we’ll have to deal with those, like, with those different things.

But you probably, even if Claude was capable of making a determination, would you want Claude to make that determination in the first place? It’s tricky, Barry, because it’s like, it’s more than just privacy. It’s like almost intimacy and it’s like tricky to reason about in a way that will make everyone comfortable.

Alessio: Yeah, I could see. You know, a virtual box, like actual virtual box app where like you run the VM and then you have like a screen within the screen, you know, you can put it in the background, but then you can like jump in the screen and like you,

Felix: that’s not a bad idea. Yeah.

Alessio: You know, like, I mean I used it, you know, people used to do it virtualizing like C Linux in a Windows machine.

Felix: Yeah.

Alessio: And like you would just jump in and then you would jump out. But it’s like, it’s not like a dual boot. It’s like within the thing. The problem is that you need twice the amount of ram, twice the amount of, you know, it’s like, it’s kind of taxing on the machine. But I think that would be cool. Kinda like see, you know, the little quad window.

I can see desktop look cute. It is clicking around things

swyx: I was gonna bring up. He’s the original machine and the machine guy, because he has the uh, windows. Windows 95 project. Where’s, where’s the Windows 85 project at?

Felix: It’s probably somewhere in my GI guitar,

swyx: right? No, no, no, no, no. It is like the first thing you see is this one.

Nice. Yeah,

Felix: yeah,

swyx: exactly.

Felix: That was honestly a very fun project though. Like, obviously I didn’t, I, I should say this, just so that No, it’s the wrong impression. I did not write the actual, the actual, obviously I didn’t build Windows only five because I was a child, but also I did not build the actual engine that is capable of like simulating an X 86 processor and JavaScript and m um, that’s a tool called V 86, which is very cool and everyone should try.

But this came out of a, this came out of like a debate we had at work where people were like, they often are in the into debating the merits of electron and whether or not we should be building software in JavaScript, yes or no. And I still am very upset that I can run all of Windows 95 in JavaScript.

And launch Microsoft Excel inside the virtualized JavaScript Windows only five machine, and do things that pro, I can do that entire chain faster than I can do a lot of other things in like traditional SaaS applications. Mm-hmm. Uh, this is sort of like a, like a performance rampage that I went on. So I’m mostly built this as a joke for some of my colleagues at Slack.

This took, took like one night. Um, what, but then that I, it was, it was not hard to do. It was all the hard work is in V 86. Yeah. Like if, go to the repo, it’s gonna say like, 99% of his work is done by, by um, a guy who goes after the, by the name. Copy. His name is Fabian.

swyx: Yeah.

Felix: Um,

swyx: cool. I think you’re, you’re kind of back on the Windows grind ‘cause you’re building out the Windows support.

Uh, I thought there was some really cool technical stories to tell. Uh, and it gives people an appreciation of like, well here’s how hard it is and here’s how important here, how, how you invested the sandbox. So maybe this is like a good opportunity to talk about something in the details.

Felix: Oh yeah, the, the VM honestly is like so cool.

There’s a lot of things we dislike about the vm, right? Like there, there’s a lot of things that are real trade offs and you want to know why you making those trade offs. Um, and you’re right, like a lot of people write me like, Hey, how, how come cloud is taking up 10 gigabytes? I could say on the point, it’s not actually taking up 10 gigabytes.

It’s just like a way that macros displays bites is like wrong, but the way we actually ride it to disc is by we collapse the empty space and the image, so it’s not actually taking up 10 gigs. But that’s a technical differentiation. That’s probably not gonna matter to, like,

swyx: to me, the the, the outcome is it takes too long to start.

Yeah. It’s like 30 seconds sometimes. So I don’t know. Oh, it should be faster than that. Whatever it be te about this feels like 30.

Felix: Yeah. Like even either way, like whatever it is, it’s going to be, it’s going to be slower than just running Log Ultra on your computer. Right. So the trade offs are real, but what we’re doing on Windows, we’re using the Windows, windows, uh, host compute system.

It’s the same thing that WSL two runs on, like the Windows subsystem for Linux that I think a lot of developers appreciate quite a bit. Yeah. Um, and it’s, it’s pretty cool because we sort of like have to separate out which system space the virtual machine runs in, in who gets to talk the virtual machine because obviously you give this virtual machine a decent amount of power.

How do we optimize not just the connection between the two systems, but also how do we make sure that random other application doesn’t get to talk to Clot inside the vm?

swyx: Hmm.

Felix: We do some pretty interesting things. Um, last week we started writing a new networking service. A networking driver. That optimizes how Claw talks to the internet.

If your company’s doing like weird internet things like pack inspection and like, like, you know, taking your part as a cell and inside your company, I think there was probably like a very small, easy version to build of cowork that is much simpler but also breaks on most com most users, computers. And this one is quite nice because it works on most users computers.

Um, and the default example I always go for is I, I really want this to be highly effective on like a, on like a machine that most people pick up. And that machine will probably not have Python, it will not have no j And even if I just take away those two things, cloud is going to be so much less effective from

swyx: your computer.

So what do you do? You don’t even, I mean, may maybe require people to install Node in Python.

Felix: Oh, like, you mean for like a, what does the feature look like without a vm?

swyx: No, no, no. So, so like, like you said, right? Let’s say a target machine is whatever’s a default spec, windows laptop.

Felix: We do this, which is quite cool.

So on, on, uh, mes, we use the, um, apple virtualization framework, which is pretty solid, optimized, like it’s good stuff, and instead simple a p call, right?

swyx: It’s

Felix: like super simple.

swyx: I, I saw the code recently and I’m like, that’s it. What the fuck

Felix: would you, once you start like shipping production code on it, you start adding like all of these edge cases, your new

swyx: Oh

Felix: yeah, it ends up being a little longer, but, um, I think Apple really cooked with a virtualization framework and it’s very, very good.

It is very fast, it’s very reliable. And same on Windows. The, the host compute system. I think WSL two as well is maybe one of the diamonds within Windows. It’s like one of the few things that developers universally rave about is very, very cool. And like hooking into the same subsystem makes a lot easier for us to say We don’t really care how locked down your computer is.

Maybe it’s like your employer’s computer and your employer has decided that you get to install nothing.

Alessio: Mm-hmm.

Felix: Not trusted, but it’s true in a lot of environments, right? Like even at Anthropic, um, our IT department controls what kinda stuff you install, just like a pretty common experience for many companies.

Um, and this gives it departments a decent amount of, like, it makes their job so much easier because we can say you can separate out cloud’s computer from the user’s computer. And then for cloud’s computer, where you probably care about its data loss, you care about like a potentially hostile actor, you care about maybe data being exfiltrated.

And once you control the network and the file system layer, you don’t really care necessarily anymore. That cloud might be writing super useful Python scripts. What worries you about the fact is that like once you install Python, now anyone can do anything on a computer. Once you put that in the vm, that risk really goes down.

swyx: Yeah.

Felix: So that’s why we jumped through all of these hoops.

swyx: Yeah. I think you, you had a different, uh, tweet about this. Um, but it, it’s, it’s almost like people have also approved exhaustion. Like, it’s like you can’t approve every single commands. Like sometimes by, by default, some of the theis, I think even early called code, uh, we have to approve every single command.

Yeah. And, and like it’s so, so there’s this sort of dichotomy between either approve every step or dangerously get permissions.

Felix: Yeah.

swyx: And actually sandboxing is like, kind of like the middle ground.

Felix: Yeah. I do think, I do think it, it’s maybe on us as like the AI industry to come up something better than, oh, this is super safe as long as it doesn’t do anything right.

Right. But if you want this to be useful, then you have to like approve every single step of the way. And like, computer use is a good example. The only way to make computer use on your host, like super safe, like really super safe is probably if you approve every single action, right. Like models, like, I would like to type the word.

You’re like, okay, that seems fine. I know, I know. Which, like cursor is focused. Yeah. It’s not

swyx: automation if you don’t delegate.

Felix: Yeah, exactly. You need to like properly delegate. You need to be able to like delegate and walk away and trust that this thing is not gonna like mess dramatically. And I don’t even think we need to build perfect systems.

I don’t think we need to wait for like a hundred percent model alignment. We can rely on the same Swiss cheese model we’ve used in the industry for a long time. But I do think we need to like universally maybe eventually invest more. And that’s what we’re doing. We need to invest more in systems where we can say, you do not need to approve everything.

swyx: Speaking of Swiss cheese model, he just wrote a thing about this.

Felix: Oh cool.

swyx: Yeah. Uh, yeah. Um, yeah. Super cool. I mean, yeah, it’s, it’s weird how like, I guess usually I think safety and security is kind of like a boring word to, to engineers. They’re like, just gimme be unsafe, gimme unsecure. But, um, I think.

Achieving the right thing. Like you are going after a consumer slash prosumer.

Felix: Yeah. Yeah. Talking both kind of like both. I think I, I also want to capture people who would’ve no trouble using clock code like yourself, right?

swyx: Yeah. Yeah.

Felix: But still find it maybe just convenient, easier. You’re like, oh cool.

That’s like the list on the right. I can edit it. Those things are just easier to do if you have

swyx: to. But this is like clearly the knowledge work side. Yeah. Claude Code will clearly capture the development workflow. But like I, I, I do think like you have to sweat this like safety and security details in order for people to trust it.

And like the even Claude and Chrome, like having the whatever API uses to do the background thing.

Felix: Yeah.

swyx: Um, that’s the only reason I use it is because otherwise I would have to just get a separate machine.

Felix: Yeah.

swyx: And just run it, run to the, and that sounds like

Felix: super annoying.

swyx: Yeah. I mean, like currently doing it, but,

Felix: and I think, I think also as developers, um, maybe we’re, we are more risk tolerant, but we’re also just like accepting we are more risk tolerant, but I think we also just have.

I don’t wanna say arrogance, but like sort of the trust that if like the really bad thing happens, we can probably fix it.

swyx: I just tell Claude to like, check with me before doing any irreversible action. Like sending an email or doing permanently. Yeah, it’s good enough.

Felix: But like, not even Claude, I mean like simple things such as NPM install, right?

Like we’re all running NPM install with full user permissions and if it wants to like read SSH, it well crazy that that is the default kind of why. Yeah, I know. I agree. I agree. Fine. Like I’m obviously doing it every single day. No, right. Like, uh, and I think obviously NPM and GitHub too have like done a pretty good job maybe over the last couple months to like clean house and come up with like more specific tokens.

But generally speaking, I think as engineers we’ve always been a little bit more risk tolerant. And if you do a little bit of introspection and you ask yourself, is that how we should be doing things, you might not always come up with the right answer. And I think for models too, like my approach, like I’m not gonna, the the safest thing is to do nothing.

We do want products that are quite capable, but to the extent possible, I don’t wanna ask you, are you okay with the script? Because I kind of believe that once it starts becoming a part of your workflow, you’re probably not either, either you don’t have the skill to understand whether or not the python, the script is safe or you’re not gonna read it anyway.

swyx: Cool. I guess a, a couple partying questions. Uh, what’s the future of clockwork?

Felix: I think we’re still, we’re still such early days. We’re gonna keep shipping things that we’re gonna keep shipping, things that, um, we’re gonna keep iterating on this thing like pretty quickly, but, which I mean, you can sort of continue to expect that every single week there’s gonna be like a small new feature, if not a big new feature.

Um, I’m going to continue probably to double down on your computer and like making you effective in your computer and making cloud effective in your computer. Um, we’re starting to grapple, as we talked about today, grapple more with a question of like, what does it mean? What does your computer mean? Does it have to be the one in front of you or like a VM on your computer or like a computer somewhere else?

And then the third thing that I’m quite excited about is. We’re continuing to go off this hill climbing on slowly taking users who are used to asking questions and getting an answer to slowly teaching them to like step more and more away. And that claw take over like bigger and bigger tasks and work both in time as well as in like scope.

And I think you can probably see most of the, our investments on our feature releases to like work on both of those things, like the ability to do more on your computer and then the ability to do more independently for longer.

swyx: Does remote control work for Claude Cowork yet? No. Right.

Felix: Excellent question.

swyx: Coming soon. I mean, that’s an obvious thing if you want to keep betting on the, on your computer, but I, to me like. You know, we, we talk about like, people are not ready this year. Like the, there’s, there’s no wall. It’s, it’s accelerating to me like what will be we be doing differently at the end of this year that, you know, we are maybe not even thinking about this, uh, at the start of this year.

Right. Like, I’m just trying to look ahead as to like, what, what’s like a good use case that you’re, that we sort of aim towards? So for, for example, for the machine learning scientists, it’s always, okay, well I want AI scientists, I can automate, automate machine learning, but like for, for knowledge work, I mean, I can already, you know, get it to sign up for Google Cloud to mean as a GI.

Felix: Yeah. ‘

swyx: cause Google cuts are, but like, what, what is, what’s beyond that? I don’t know.

Felix: I think it’s basically the idea that like you still had to tell her to build your script, right? He was still kind of involved.

swyx: Yes.

Felix: In maybe a way that felt kind of magical to you, but like, maybe to me on the other side is the person building this product still feels kind of heavy handed.

I see so much process that I’m like, oh, lemme take that away from you. Okay. But like, how do I just go, I will continues to go or continue to go like further and further up the stack. Make your life easier and easier.

swyx: Oh, here’s one. Right?

Felix: Yeah.

swyx: Watch, uh, I, you know, I don’t care about my own privacy or whatever, or I trust cloud, I trust philanthropic.

So just watch everything I do on a normal day-to-day basis. At the end of the day, tell me what you is called co workable.

Felix: Yeah. I

swyx: dunno.

Felix: I think the funny thing about a lot of these products is that like, for good reason, I don’t enjoy, I, I don’t, throughout my entire career, I’ve never like teased too much what I’m working on because I think you should just like, yeah.

Release it. Yeah. Build the base and release it, and then talk about it. Like I’m, I’m not a big fan of the like vague posting my own work ahead of time.

swyx: Yeah.

Felix: But the thing that is like always so fascinating to me is like, both of you all multiple times a day, you’ve like mentioned things and I’m like, yeah, that is obviously like very obvious

swyx: Okay.

Felix: That someone should be working on those things. Um, and I think we’re still in the space where if you look at cowork. The things that we will be releasing will probably not be a big surprise to either of you. You’re gonna be like, yeah, obviously that’s valuable obviously that we’re working on those things.

swyx: Yeah.

Yeah.

Felix: And obviously that’s good and useful. And the more I hit those points, the more our features fit into that category, I think the better it is for us because then we don’t end up building things that are too hyper specialized to difficult harness style.

swyx: Yeah. I think the hyper specialized thing is very important.

It keeps you like general purpose. It, it means you’re not thinking too small. Maybe I don’t, I don’t know what the, the word is.

Felix: Yeah, yeah, exactly. It’s like the whole concept that like at no point if we release, you know, there’s no Claude Code for no jazz applications that use React and 10 Stack. I know any of those two things.

And like if it’s anything else, I know several startups like that. I think that’s pretty, like, I’m not a vc, I’m not an investor. It’s like hard for me to predict where the markets go. But in terms of the building box that I’m interested in, the electron is probably by far the most popular thing I ever built.

And, um, electron itself is like. Very abstractable and generalizable. Right? Like so many apps run in it. And I think it would’ve been hard for me to predict how many apps actually end up using Electron.

swyx: Yeah.

Felix: Um, and what would’ve been even less useful for me to predict this in what those apps do. I distinctly remember a bloom coming out of being like, that is cool.

Like you are a camera in a little circle in the corner. That is pretty smart.

swyx: That’s an app. Yeah. Yeah.

Felix: Or at least was, I’m not sure if it still is. It was for a while. Or like one password has so many interesting things. Right. It, it’s, it’s, it’s a level of the stack that I’m quite comfortable with. And whenever I give other engineers, advisors actually that layer that I think is most valuable to invest in because the tools of that layer are not that good.

But that’s where you get the most leverage

swyx: for like,

Felix: the future in general.

swyx: Just quick tangent on Electron. ‘cause I always wonder this, uh, have you looked at Tori?

Felix: I have, yeah.

swyx: What’s your take? Uh, you know, look, my, my my, my view is like most things should be Tori by default, unless you really need the full power of electron, but.

Felix: Yeah, I can give like my take on, I can give my big take. Why do we ship an entire version of chromium inside the thing, right? Like why do we do that? And, um, people ask me this question a lot because it’s like very counterintuitive. Wouldn’t it be much easier to use the web use that are on the operating system?

Wouldn’t it be much easier not to have to do that? And the answer is yes. And like obviously I did that once upon a time. I did that there was a version of the Slack app that used just the operating system that use Wait, did you, did you start the Slack app? I would, well, team effort and

swyx: Yeah, but I was, I was there.

We built the Slack app.

Felix: Yeah. It’s crazy. Um, I mean obviously you get the electron guy to do it, but, well, but this is an interesting point. Like, by the time, by the time I joined Slack, they already had an app that was built with something at the time called Met Gap. It was a little bit like the same app gap thing for mobile.

It just used the operating systems. Web views. Um, and that didn’t work for like so many reasons. Um, and they were like, all right, maybe we need like bigger guns. We need to like take more control of the rendering stack. And there’s, there’s a few things I always mention here. Um, I think if you’re building a small app, just going with the operating systems web view is perfectly fine.

If you’re building an app, maybe that doesn’t have too many users who will like cry bloody murder. If it doesn’t work, that is fine. The reason to go with your own embedded rendering engine is because, and this is still true in 2026, the operating system render engines are not that good. They’re just not that good.

Both Microsoft and Apple are trying to move away from that. They so far really haven’t, the only way to upgrade those is to upgrade your operating system. So if you are, say Slack and you have critical rendering bug in WK WebU and some of the other WebU options, your only recourse is to tell your customer, oh, sorry, you’re too poor.

You didn’t bother the, its MacBook. Unacceptable.

swyx: Mm-hmm.

Felix: Unacceptable to user, unacceptable to user developer. So you sort of need to like go down the stack and like find the best rendering engine, then put it in your app. Why chromium, even though it’s very big chromium is by far the best thing. Like I, I often like to remind people the unreal engine, you wanna render some text.

They use chromium. Like chromium is part of the unreal engine for same purposes. Chromium is very, very good. I think it’s like one of the marvels of engineering. It’s very hard for, we’re in San Francisco right now where we’re recording. Most of the people in the city are web developers. It’s hard for me to like overstate how magical it is.

They run seat like rendering a YouTube video dynamically. Negotiating a bit rate, figuring out what to do about your extremely broken hardware driver. Actually, this is a fun thing. Um, okay, you can enter Chrome call on Wack Wack GPU. Okay? And if you scroll down a little bit, these are all the enabled workarounds because something is going wrong on your computer.

If you’re doing this on a Windows computer with like A GPU, that is not the most popular GPO, it will be much longer. And all of these are usually just there to make sure that if I say as a developer, I want a red pixel to appear here, that that actually happens. Chrome is such a marvel because of works on all the machines that user might throw you and it’s gonna work fairly reliably.

And if it doesn’t, they will probably fix it within 24 hours.

swyx: I see. So this is the super operating system, right? That that works everywhere.

Felix: Yeah.

swyx: Right. Okay. Yeah.

Felix: So a lot of the magic of Electron is honestly just that it makes it very easy for you to ch chromium in a way that serves you exactly in your use cases.

Elect, uh, exactly.

swyx: Our next interview is with Morgan Dreesen.

Felix: Yeah.

swyx: Who had the phrase like, desktop OSS are just poorly deep, uh, poor implications of the, the actual os, which is Chrome, which like actually works everywhere. And this is this, this is the platform where you ship apps.

Felix: I, I think the wild thing is that like as engineers, we so often sort of assume that the platform, like the layer below us is like super stable.

Mm-hmm. And then you talk to those people and they’re like, ah, we are also just like guessing. Um, uh, and I had like a distinct moment at Slack where one of our customers at Slack was Nvidia, and for a while I really put GPU developers on this pedestal in my head. And I do think they’re still probably much smarter than I am.

But I was like hardware engineers who built the chips, who then like built the drivers. Their work must be so much harder than mine. They must be very good. And we had like one bug in Slack where like if you had a YouTube video in Slack, it wouldn’t quite render why. Like it would have these weird artifacts.

And, um, that ended up being a chromium bug. And I ended up on this like giant thread. So I got to see a lot of the source code. And they also are just like common to do. We don’t know why this is weird, but if you flip this bit, things work. You know, this is just like happening with every layer of the stack.

Maybe the, uh, you know, the,

swyx: the end of year a GI prediction is that clock can build chromium. You see, you see you, you laugh now. But yeah, like, you know, someday

Felix: it’s, it’s sounding, it could get pretty good. Like it used to be completely useless. Um, mostly just like overwhelmed, both with how hyper specialized tools are inside the chromium repo.

Like for, for a long time. Chrome has like sort of reinvent all the tools because none of them are capable of ending Chrome. I think the EGI moment I am kind of waiting for is at what point are we gonna say Electron is probably no longer necessary because you can just build fully native apps. The Swifty?

Yeah. Like not just in Swift because this is one thing, like it’s pretty easy if you, I think our current models are quite capable of taking an electron app and replicating it Swift, are they gonna be capable of like building an app that is actually more performant, which is less memory? All of that stuff, um, is gonna go into the same hyper optimization that developers have done for like a long time.

We’re not quite there yet. Work and like point even our best models at a thing and say, just replicate this, a native code. Make no mistakes. Ultra think. Right? We’re not quite there yet. Um, ultra

swyx: think is bad

Felix: today. Think is back. Yes. Okay.

swyx: Or we’ll get an ultra think for like days,

Felix: just a pretty long time before,

swyx: but he worked on Ultra think for days.

Yeah. Why he just, it’s just. Front,

Alessio: I’ll let it, the

Felix: more goes into

swyx: it. Yeah. Okay.

Alessio: Another question I had is like coworks. So if I have my Claude Cowork, like what’s kinda like the multiplayer mode? I think sub agents is like single player Split up the context.

Felix: Yeah.

Alessio: And the multiplayer cowork is like, my colleague is some file on their machine that I wanna know about or I wanna know how their task is going to then update my thing.

Like is that interesting? Is that something that makes sense for you to build or for like

Felix: It’s like super interesting to me it, it almost goes back to like some of the scaffolding room. Like okay, are we gonna be end up, are we, will we end up building scaffolding that will just go away? And like a question I have here is at what point do we just assign these things, like their own Gmail account?

We just give them their like Slack handle and then they will just like use the same tools we humans use to interact with each other. You mentioned our finance people, they’ve been working pretty hard on very good office integrations. And I think for a while we’ve been like, we built so much tech around cloud, leaving useful comments inside a Google Doc, and now it just does, it just like leaves a comment in your Google Doc and that’s how you interact with it.

Maybe like the similar thing where I still have open questions around what is the best interaction mode? Is it for us to build something super custom for cowork agents to talk to each other? Or is it okay, let’s just jump straight to the finish line and say, well, we’re just gonna give this thing, if you use Slack at work, we’re just gonna give this thing a Slack handle.

And that’s going to be the way, it’s like multiplayer capable.

Alessio: They communicate with each other. Yeah. Yeah. Like, you know, as a, as a fun project, I build this thing called piq, which basically takes any repo and the PI agent, uh, coding agent, it puts it in a VPS, and then there’s a public web hook where anybody can submit a coding task.

Oh. And then there’s a dashboard in which you review the task and then piq pi, pi, uh, queue.

Yeah. You basically get all these like tasks, anybody can submit a task.

Felix: Mm-hmm.

Alessio: And to me it’s almost like in the organization of the future, it’s like the sales people are talking to the engineering team that is talking to the marketing team, to the product team, and all these coworker are going to like queue up decisions for other people to approve in a way.

Felix: Yeah.

Alessio: You know, and I’m kind of curious what that looks like and like how do you, how do I give my cowork the ability to build a proof task without asking me

Felix: Yeah.

Alessio: And how to decide which one I need to review. Yeah. You know, because for some of these things it’s like, you know, you wanna change the color of something that’s kinda like a branding decision.

Or another one is like, hey, your thing is just broken. It’s like, this is like how you fix it. Yeah. And Claude can actually review whether or not that prompt matches what he’s trying to do today. Everything is still very, it’s like multiplayer within the single player, you know? Yeah. I guess spin up many of them, but like, how do I get multiple people to hand off to each other things using their particular context?

Felix: Yeah. And for both of your coworkers to like talk to each other. Right,

Alessio: right. Yeah. Hey, we got an episode today. Can you like, have you, you know, or

Felix: Yeah. This is like a, uh, I know we’re like running out of time here, but like we, we previously talked about sharing skills and I did have this question of like, what if your cowork would just like ask the other coworks if they have a skill for this task?

Doesn’t matter. These could do.

swyx: Right. Like, okay, so skill transfer.

Felix: Yeah, like,

swyx: um, and again, that’s, maybe

Felix: this maybe goes back into the territory of like building something very powerful and building something creepy often goes hand in hand. Um, because I could tell from the reaction that my fellow engineers said that this is probably not what we’re gonna do, but like.

We have Bluetooth le right? Like I, this computer can figure out that it’s sitting right next to this computer. So you’re probably working on the same thing. Um, well, you see that in cowork, probably not. But, um, there’s like, I think really creative solutions to problems that we really haven’t tried yet.

Yeah,

Alessio: yeah, yeah. Yeah.

swyx: Excellent. I guess the, the last thing is, uh, philanthropic labs. Uh, I always have this mental model of a model lab versus, uh, agent lab. And this is basically Anthropics internal agent lab, which co Claude Code, uh, is now under, right? It’s part of the whole org.

Felix: I mean, people are so fungible, right?

Like,

swyx: okay, this is just, I, I don’t know how, I don’t know real. This is, I don’t know.

Felix: No, it’s a real team. It’s a very, um, the, the last team is primarily working though on things that you don’t see in public yet. Um, they’re trying like really wild out there, ideas that seem quite improbable. Um, the mad science

swyx: thing.

But you, you’re, are you officially under this thing or

Felix: No? We’re, where is the Claude Code is, but now Claude Code is like a fairly big group where. I actually know many people we are like, like I remember yesterday coming into our weekly COVID meeting. I was like, woo,

Alessio: this is hot.

Felix: There’s a lot of people here.

Um, but we still have a labs team and we actually made the labs team a lot bigger. Mike just joined the labs team as a, as an ic, which I think is very cool and very fun. But they’re, they’re working on things that you have not seen yet that are extremely out there and probably half broken. Right? Like the sort of the idea of a lab team is that it should only work on things that make really no sense for anyone else to work on.

swyx: Okay. Well, looking for exciting things from there, but thank you so much. I know we’re out of time, but uh, appreciate your joining us. I appreciate co cowork, everyone go use it. Uh, it is the closest I’ve felt to a I this year. That’s so nice you to say. Thank you very much. Yeah. Thank you for your time. Yeah.
Discussion about this episodeCommentsRestacks
Latent Space: The AI Engineer PodcastThe podcast by and for AI Engineers! In 2025, over 10 million readers and listeners came to Latent Space to hear about news, papers and interviews in Software 3.0.We cover Foundation Models changing every domain in Code Generation, Multimodality, AI Agents, GPU Infra and more, directly from the founders, builders, and thinkers involved in pushing the cutting edge. Striving to give you both the definitive take on the Current Thing down to the first introduction to the tech you'll be using in the next 3 months! We break news and exclusive interviews from OpenAI, Anthropic, Gemini, Meta (Soumith Chintala), Sierra (Bret Taylor), tiny (George Hotz), Databricks/MosaicML (Jon Frankle), Modular (Chris Lattner), Answer.ai (Jeremy Howard), et al. Full show notes always on https://latent.spaceThe podcast by and for AI Engineers! In 2025, over 10 million readers and listeners came to Latent Space to hear about news, papers and interviews in Software 3.0.

We cover Foundation Models changing every domain in Code Generation, Multimodality, AI Agents, GPU Infra and more, directly from the founders, builders, and thinkers involved in pushing the cutting edge. Striving to give you both the definitive take on the Current Thing down to the first introduction to the tech you'll be using in the next 3 months! We break news and exclusive interviews from OpenAI, Anthropic, Gemini, Meta (Soumith Chintala), Sierra (Bret Taylor), tiny (George Hotz), Databricks/MosaicML (Jon Frankle), Modular (Chris Lattner), Answer.ai (Jeremy Howard), et al. 

Full show notes always on https://latent.spaceSubscribeListen onSubstack AppApple PodcastsSpotifyRSS FeedRecent Episodes

Mistral: Voxtral TTS, Forge, Leanstral, & what's next for Mistral 4 — w/ Pavan Kumar Reddy & Guillaume LampleMar 30

🔬Why There Is No "AlphaFold for Materials" — AI for Materials Discovery with Heather KulikMar 24 • Brandon Anderson and RJ Honicky

Dreamer: the Personal Agent OS — David SingletonMar 20

Retrieval After RAG: Hybrid Search, Agents, and Database Design — Simon Hørup Eskildsen of TurbopufferMar 12

NVIDIA's AI Engineers: Agent Inference at Planetary Scale and "Speed of Light" — Nader Khalil (Brev), Kyle Kranen (Dynamo)Mar 10

Cursor's Third Era: Cloud AgentsMar 6

Every Agent Needs a Box — Aaron Levie, BoxMar 5
## Ready for more?
Subscribe© 2026 Latent.Space · Privacy ∙ Terms ∙ Collection notice

 Start your SubstackGet the appSubstack is the home for great culture
 

 
 
 
 

 
 
 
 
 window._preloads = JSON.parse("{\"isEU\":false,\"language\":\"en\",\"country\":\"US\",\"userLocale\":{\"language\":\"en\",\"region\":\"US\",\"source\":\"default\"},\"base_url\":\"https://www.latent.space\",\"stripe_publishable_key\":\"pk_live_51QfnARLDSWi1i85FBpvw6YxfQHljOpWXw8IKi5qFWEzvW8HvoD8cqTulR9UWguYbYweLvA16P7LN6WZsGdZKrNkE00uGbFaOE3\",\"captcha_site_key\":\"6LeI15YsAAAAAPXyDcvuVqipba_jEFQCjz1PFQoz\",\"pub\":{\"apple_pay_disabled\":false,\"apex_domain\":null,\"author_id\":89230629,\"byline_images_enabled\":true,\"bylines_enabled\":true,\"chartable_token\":null,\"community_enabled\":true,\"copyright\":\"Latent.Space\",\"cover_photo_url\":null,\"created_at\":\"2022-09-12T05:38:09.694Z\",\"custom_domain_optional\":false,\"custom_domain\":\"www.latent.space\",\"default_comment_sort\":\"best_first\",\"default_coupon\":null,\"default_group_coupon\":\"26e3a27d\",\"default_show_guest_bios\":true,\"email_banner_url\":null,\"email_from_name\":\"Latent.Space\",\"email_from\":null,\"embed_tracking_disabled\":false,\"explicit\":false,\"expose_paywall_content_to_search_engines\":true,\"fb_pixel_id\":null,\"fb_site_verification_token\":null,\"flagged_as_spam\":false,\"founding_subscription_benefits\":[\"If we've meaningfully impacted your work/thinking!\"],\"free_subscription_benefits\":[\"All podcasts + public/guest posts\"],\"ga_pixel_id\":null,\"google_site_verification_token\":null,\"google_tag_manager_token\":null,\"hero_image\":null,\"hero_text\":\"The AI Engineer newsletter + Top technical AI podcast. How leading labs build Agents, Models, Infra, & AI for Science. See https://latent.space/about for highlights from Greg Brockman, Andrej Karpathy, George Hotz, Simon Willison, Soumith Chintala et al!\",\"hide_intro_subtitle\":null,\"hide_intro_title\":null,\"hide_podcast_feed_link\":false,\"homepage_type\":\"magaziney\",\"id\":1084089,\"image_thumbnails_always_enabled\":false,\"invite_only\":false,\"hide_podcast_from_pub_listings\":false,\"language\":\"en\",\"logo_url_wide\":\"https://substackcdn.com/image/fetch/$s_!1PJi!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa4fe1182-38af-4a5d-bacc-439c36225e87_5000x1200.png\",\"logo_url\":\"https://substackcdn.com/image/fetch/$s_!DbYa!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F73b0838a-bd14-46a1-801c-b6a2046e5c1e_1130x1130.png\",\"minimum_group_size\":2,\"moderation_enabled\":true,\"name\":\"Latent.Space\",\"paid_subscription_benefits\":[\"Support the podcast and newsletter work we do!\",\"Weekday full AINews!\"],\"parsely_pixel_id\":null,\"chartbeat_domain\":null,\"payments_state\":\"enabled\",\"paywall_free_trial_enabled\":true,\"podcast_art_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/534f41b9-5d2b-49b9-9578-4852473c362f_1400x1400.png\",\"paid_podcast_episode_art_url\":null,\"podcast_byline\":\"Latent.Space\",\"podcast_description\":\"The podcast by and for AI Engineers! In 2025, over 10 million readers and listeners came to Latent Space to hear about news, papers and interviews in Software 3.0.\\n\\nWe cover Foundation Models changing every domain in Code Generation, Multimodality, AI Agents, GPU Infra and more, directly from the founders, builders, and thinkers involved in pushing the cutting edge. Striving to give you both the definitive take on the Current Thing down to the first introduction to the tech you'll be using in the next 3 months! We break news and exclusive interviews from OpenAI, Anthropic, Gemini, Meta (Soumith Chintala), Sierra (Bret Taylor), tiny (George Hotz), Databricks/MosaicML (Jon Frankle), Modular (Chris Lattner), Answer.ai (Jeremy Howard), et al. \\n\\nFull show notes always on https://latent.space\",\"podcast_enabled\":true,\"podcast_feed_url\":null,\"podcast_title\":\"Latent Space: The AI Engineer Podcast\",\"post_preview_limit\":200,\"primary_user_id\":89230629,\"require_clickthrough\":false,\"show_pub_podcast_tab\":false,\"show_recs_on_homepage\":true,\"subdomain\":\"swyx\",\"subscriber_invites\":0,\"support_email\":null,\"theme_var_background_pop\":\"#0068EF\",\"theme_var_color_links\":true,\"theme_var_cover_bg_color\":null,\"trial_end_override\":null,\"twitter_pixel_id\":null,\"type\":\"newsletter\",\"post_reaction_faces_enabled\":true,\"is_personal_mode\":false,\"plans\":[{\"id\":\"yearly80usd\",\"object\":\"plan\",\"active\":true,\"aggregate_usage\":null,\"amount\":8000,\"amount_decimal\":\"8000\",\"billing_scheme\":\"per_unit\",\"created\":1693620604,\"currency\":\"usd\",\"interval\":\"year\",\"interval_count\":1,\"livemode\":true,\"metadata\":{\"substack\":\"yes\"},\"meter\":null,\"nickname\":\"$80 a year\",\"product\":\"prod_OYqzb0iIwest4i\",\"tiers\":null,\"tiers_mode\":null,\"transform_usage\":null,\"trial_period_days\":null,\"usage_type\":\"licensed\",\"currency_options\":{\"aud\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":12000,\"unit_amount_decimal\":\"12000\"},\"brl\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":44500,\"unit_amount_decimal\":\"44500\"},\"cad\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":11000,\"unit_amount_decimal\":\"11000\"},\"chf\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":6500,\"unit_amount_decimal\":\"6500\"},\"dkk\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":51000,\"unit_amount_decimal\":\"51000\"},\"eur\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":7000,\"unit_amount_decimal\":\"7000\"},\"gbp\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":6000,\"unit_amount_decimal\":\"6000\"},\"mxn\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":144500,\"unit_amount_decimal\":\"144500\"},\"nok\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":81000,\"unit_amount_decimal\":\"81000\"},\"nzd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":14000,\"unit_amount_decimal\":\"14000\"},\"pln\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":29000,\"unit_amount_decimal\":\"29000\"},\"sek\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":74000,\"unit_amount_decimal\":\"74000\"},\"usd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":8000,\"unit_amount_decimal\":\"8000\"}}},{\"id\":\"monthly8usd\",\"object\":\"plan\",\"active\":true,\"aggregate_usage\":null,\"amount\":800,\"amount_decimal\":\"800\",\"billing_scheme\":\"per_unit\",\"created\":1693620602,\"currency\":\"usd\",\"interval\":\"month\",\"interval_count\":1,\"livemode\":true,\"metadata\":{\"substack\":\"yes\"},\"meter\":null,\"nickname\":\"$8 a month\",\"product\":\"prod_OYqz6hS4QhIgDK\",\"tiers\":null,\"tiers_mode\":null,\"transform_usage\":null,\"trial_period_days\":null,\"usage_type\":\"licensed\",\"currency_options\":{\"aud\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":1200,\"unit_amount_decimal\":\"1200\"},\"brl\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":4500,\"unit_amount_decimal\":\"4500\"},\"cad\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":1100,\"unit_amount_decimal\":\"1100\"},\"chf\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":700,\"unit_amount_decimal\":\"700\"},\"dkk\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":5500,\"unit_amount_decimal\":\"5500\"},\"eur\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":700,\"unit_amount_decimal\":\"700\"},\"gbp\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":600,\"unit_amount_decimal\":\"600\"},\"mxn\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":14500,\"unit_amount_decimal\":\"14500\"},\"nok\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":8500,\"unit_amount_decimal\":\"8500\"},\"nzd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":1400,\"unit_amount_decimal\":\"1400\"},\"pln\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":2900,\"unit_amount_decimal\":\"2900\"},\"sek\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":7500,\"unit_amount_decimal\":\"7500\"},\"usd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":800,\"unit_amount_decimal\":\"800\"}}},{\"id\":\"founding12300usd\",\"name\":\"founding12300usd\",\"nickname\":\"founding12300usd\",\"active\":true,\"amount\":12300,\"currency\":\"usd\",\"interval\":\"year\",\"interval_count\":1,\"metadata\":{\"substack\":\"yes\",\"founding\":\"yes\",\"no_coupons\":\"yes\",\"short_description\":\"Latent Spacenaut\",\"short_description_english\":\"Latent Spacenaut\",\"minimum\":\"12300\",\"minimum_local\":{\"aud\":18000,\"brl\":64000,\"cad\":17500,\"chf\":10000,\"dkk\":79500,\"eur\":11000,\"gbp\":9500,\"mxn\":220500,\"nok\":119500,\"nzd\":21500,\"pln\":46000,\"sek\":116500,\"usd\":12500}},\"currency_options\":{\"aud\":{\"unit_amount\":18000,\"tax_behavior\":\"unspecified\"},\"brl\":{\"unit_amount\":64000,\"tax_behavior\":\"unspecified\"},\"cad\":{\"unit_amount\":17500,\"tax_behavior\":\"unspecified\"},\"chf\":{\"unit_amount\":10000,\"tax_behavior\":\"unspecified\"},\"dkk\":{\"unit_amount\":79500,\"tax_behavior\":\"unspecified\"},\"eur\":{\"unit_amount\":11000,\"tax_behavior\":\"unspecified\"},\"gbp\":{\"unit_amount\":9500,\"tax_behavior\":\"unspecified\"},\"mxn\":{\"unit_amount\":220500,\"tax_behavior\":\"unspecified\"},\"nok\":{\"unit_amount\":119500,\"tax_behavior\":\"unspecified\"},\"nzd\":{\"unit_amount\":21500,\"tax_behavior\":\"unspecified\"},\"pln\":{\"unit_amount\":46000,\"tax_behavior\":\"unspecified\"},\"sek\":{\"unit_amount\":116500,\"tax_behavior\":\"unspecified\"},\"usd\":{\"unit_amount\":12500,\"tax_behavior\":\"unspecified\"}}}],\"stripe_user_id\":\"acct_1B3pNWKWe8hdGUWL\",\"stripe_country\":\"SG\",\"stripe_publishable_key\":\"pk_live_51B3pNWKWe8hdGUWL8wfT91ugrzbIB6qFqnTzHiUzKR5Sjtm52KIOo0M5yhuAokI02qFay5toW4QfOsJttHMoBivF003gbn4zNC\",\"stripe_platform_account\":\"US\",\"automatic_tax_enabled\":false,\"author_name\":\"Latent.Space\",\"author_handle\":\"swyx\",\"author_photo_url\":\"https://substackcdn.com/image/fetch/$s_!drTb!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdb0f8d45-1eb8-4c02-a120-650d377ee52d_640x640.jpeg\",\"author_bio\":\"Writer, curator, latent space explorer. Main blog: https://swyx.io Devrel/Dev community: https://dx.tips/ Twitter: https://twitter.com/swyx\",\"twitter_screen_name\":\"swyx\",\"has_custom_tos\":false,\"has_custom_privacy\":false,\"theme\":{\"background_pop_color\":\"#9333ea\",\"web_bg_color\":\"#ffffff\",\"cover_bg_color\":\"#ffffff\",\"publication_id\":1084089,\"color_links\":null,\"font_preset_heading\":\"slab\",\"font_preset_body\":\"sans\",\"font_family_headings\":null,\"font_family_body\":null,\"font_family_ui\":null,\"font_size_body_desktop\":null,\"print_secondary\":null,\"custom_css_web\":null,\"custom_css_email\":null,\"home_hero\":\"magaziney\",\"home_posts\":\"custom\",\"home_show_top_posts\":true,\"hide_images_from_list\":false,\"home_hero_alignment\":\"left\",\"home_hero_show_podcast_links\":true,\"default_post_header_variant\":null,\"custom_header\":null,\"custom_footer\":null,\"social_media_links\":null,\"font_options\":null,\"section_template\":null,\"custom_subscribe\":null},\"threads_v2_settings\":{\"photo_replies_enabled\":true,\"first_thread_email_sent_at\":null,\"create_thread_minimum_role\":\"paid\",\"activated_at\":\"2025-09-09T23:28:56.695+00:00\",\"reader_thread_notifications_enabled\":false,\"boost_free_subscriber_chat_preview_enabled\":false,\"push_suppression_enabled\":false},\"default_group_coupon_percent_off\":\"49.00\",\"pause_return_date\":null,\"has_posts\":true,\"has_recommendations\":true,\"first_post_date\":\"2022-09-17T20:35:46.224Z\",\"has_podcast\":true,\"has_free_podcast\":true,\"has_subscriber_only_podcast\":true,\"has_community_content\":true,\"rankingDetail\":\"Thousands of paid subscribers\",\"rankingDetailFreeIncluded\":\"Hundreds of thousands of subscribers\",\"rankingDetailOrderOfMagnitude\":1000,\"rankingDetailFreeIncludedOrderOfMagnitude\":100000,\"rankingDetailFreeSubscriberCount\":\"Over 176,000 subscribers\",\"rankingDetailByLanguage\":{\"ca\":{\"rankingDetail\":\"Milers de subscriptors de pagament\"},\"da\":{\"rankingDetail\":\"Tusindvis af betalte abonnenter\"},\"de\":{\"rankingDetail\":\"Tausende von Paid-Abonnenten\"},\"es\":{\"rankingDetail\":\"Miles de suscriptores de pago\"},\"fr\":{\"rankingDetail\":\"Plusieurs milliers d\u2019abonn\u00E9s payants\"},\"ja\":{\"rankingDetail\":\"\u6570\u5343\u4EBA\u306E\u6709\u6599\u767B\u9332\u8005\"},\"nb\":{\"rankingDetail\":\"Tusenvis av betalende abonnenter\"},\"nl\":{\"rankingDetail\":\"Duizenden betalende abonnees\"},\"pl\":{\"rankingDetail\":\"Tysi\u0105ce p\u0142ac\u0105cych subskrybent\u00F3w\"},\"pt\":{\"rankingDetail\":\"Milhares de subscri\u00E7\u00F5es pagas\"},\"pt-br\":{\"rankingDetail\":\"Milhares de assinantes pagas\"},\"it\":{\"rankingDetail\":\"Migliaia di abbonati a pagamento\"},\"tr\":{\"rankingDetail\":\"Binlerce \u00FCcretli abone\"},\"sv\":{\"rankingDetail\":\"Tusentals betalande prenumeranter\"},\"en\":{\"rankingDetail\":\"Thousands of paid subscribers\"}},\"freeSubscriberCount\":\"176,000\",\"freeSubscriberCountOrderOfMagnitude\":\"176K+\",\"author_bestseller_tier\":1000,\"author_badge\":{\"type\":\"bestseller\",\"tier\":1000},\"disable_monthly_subscriptions\":false,\"disable_annual_subscriptions\":false,\"hide_post_restacks\":false,\"notes_feed_enabled\":false,\"showIntroModule\":false,\"isPortraitLayout\":false,\"last_chat_post_at\":\"2025-09-16T10:15:58.593Z\",\"primary_profile_name\":\"Latent.Space\",\"primary_profile_photo_url\":\"https://substackcdn.com/image/fetch/$s_!drTb!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdb0f8d45-1eb8-4c02-a120-650d377ee52d_640x640.jpeg\",\"no_follow\":false,\"paywall_chat\":\"free\",\"sections\":[{\"id\":327741,\"created_at\":\"2026-01-23T16:38:15.607Z\",\"updated_at\":\"2026-02-06T00:29:08.963Z\",\"publication_id\":1084089,\"name\":\"AINews: Weekday Roundups\",\"description\":\"Every Weekday - human-curated, AI-summarized news recaps across all of AI Engineering. See https://www.youtube.com/watch?v=IHkyFhU6JEY for how it works\",\"slug\":\"ainews\",\"is_podcast\":false,\"is_live\":true,\"is_default_on\":true,\"sibling_rank\":2,\"port_status\":\"success\",\"logo_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/9a9e98c6-5aeb-461b-b5d0-54d75773e5fa_124x124.png\",\"hide_from_navbar\":false,\"email_from_name\":\"AINews\",\"hide_posts_from_pub_listings\":true,\"email_banner_url\":null,\"cover_photo_url\":null,\"hide_intro_title\":false,\"hide_intro_subtitle\":false,\"ignore_publication_email_settings\":false,\"custom_config\":{},\"showLinks\":[],\"spotifyPodcastSettings\":null,\"podcastSettings\":null,\"pageTheme\":{\"id\":85428,\"publication_id\":1084089,\"section_id\":327741,\"page\":null,\"page_hero\":\"default\",\"page_posts\":\"list\",\"show_podcast_links\":true,\"hero_alignment\":\"left\"},\"podcastPalette\":{\"DarkMuted\":{\"population\":72,\"rgb\":[73,153,137]},\"DarkVibrant\":{\"population\":6013,\"rgb\":[4,100,84]},\"LightMuted\":{\"population\":7,\"rgb\":[142,198,186]},\"LightVibrant\":{\"population\":3,\"rgb\":[166,214,206]},\"Muted\":{\"population\":6,\"rgb\":[92,164,156]},\"Vibrant\":{\"population\":5,\"rgb\":[76,164,146]}},\"spotify_podcast_settings\":null},{\"id\":335089,\"created_at\":\"2026-02-06T00:32:12.973Z\",\"updated_at\":\"2026-02-10T09:26:47.072Z\",\"publication_id\":1084089,\"name\":\"Latent Space: AI for Science\",\"description\":\"a dedicated channel for Latent Space's AI for Science essays that do not get sent to the broader engineering audience \u2014 opt in if high interest in AI for Science!\",\"slug\":\"cience\",\"is_podcast\":false,\"is_live\":true,\"is_default_on\":true,\"sibling_rank\":3,\"port_status\":\"success\",\"logo_url\":null,\"hide_from_navbar\":false,\"email_from_name\":\"Latent Space Science\",\"hide_posts_from_pub_listings\":false,\"email_banner_url\":null,\"cover_photo_url\":null,\"hide_intro_title\":false,\"hide_intro_subtitle\":false,\"ignore_publication_email_settings\":false,\"custom_config\":{},\"showLinks\":[],\"spotifyPodcastSettings\":null,\"podcastSettings\":null,\"pageTheme\":null,\"podcastPalette\":{\"DarkMuted\":{\"population\":72,\"rgb\":[73,153,137]},\"DarkVibrant\":{\"population\":6013,\"rgb\":[4,100,84]},\"LightMuted\":{\"population\":7,\"rgb\":[142,198,186]},\"LightVibrant\":{\"population\":3,\"rgb\":[166,214,206]},\"Muted\":{\"population\":6,\"rgb\":[92,164,156]},\"Vibrant\":{\"population\":5,\"rgb\":[76,164,146]}},\"spotify_podcast_settings\":null}],\"didIdentity\":\"did:plc:es3srknleppmlecmx45g2hoe\",\"multipub_migration\":null,\"navigationBarItems\":[{\"id\":\"ccf2f42a-8937-4639-b19f-c9f4de0e156c\",\"publication_id\":1084089,\"sibling_rank\":0,\"link_title\":null,\"link_url\":null,\"section_id\":null,\"post_id\":null,\"is_hidden\":true,\"standard_key\":\"archive\",\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"b729d56f-08c1-4100-ab1a-205d81648d74\",\"publication_id\":1084089,\"sibling_rank\":1,\"link_title\":null,\"link_url\":null,\"section_id\":null,\"post_id\":null,\"is_hidden\":true,\"standard_key\":\"leaderboard\",\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"8beddb9c-dd08-4f26-8ee0-b070c1512234\",\"publication_id\":1084089,\"sibling_rank\":2,\"link_title\":\"YouTube\",\"link_url\":\"https://www.youtube.com/playlist?list=PLWEAb1SXhjlfkEF_PxzYHonU_v5LPMI8L\",\"section_id\":null,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"32147b98-9d0e-4489-9749-a205af5d5880\",\"publication_id\":1084089,\"sibling_rank\":3,\"link_title\":\"X\",\"link_url\":\"https://x.com/latentspacepod\",\"section_id\":null,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"eb9e689e-85ee-41b2-af34-dd39a2056c7b\",\"publication_id\":1084089,\"sibling_rank\":4,\"link_title\":\"Discord & Meetups\",\"link_url\":\"\",\"section_id\":null,\"post_id\":115665083,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":{\"id\":115665083,\"slug\":\"community\",\"title\":\"Join the Latent.Space Community!\",\"type\":\"page\"},\"section\":null,\"children\":[]},{\"id\":\"338b842e-22f3-4c36-aa92-1c7ebea574d2\",\"publication_id\":1084089,\"sibling_rank\":7,\"link_title\":\"Write for us!\",\"link_url\":\"https://docs.google.com/forms/d/e/1FAIpQLSeHQAgupNkVRgjNfMJG9d7SFTWUytdS6SNCJVkd0SMNMXHHwA/viewform\",\"section_id\":null,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"fc1a55a0-4a35-46e2-8f57-23b3b668d2cc\",\"publication_id\":1084089,\"sibling_rank\":9999,\"link_title\":null,\"link_url\":null,\"section_id\":335089,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":{\"id\":335089,\"slug\":\"cience\",\"name\":\"Latent Space: AI for Science\",\"hide_from_navbar\":false,\"is_podcast\":false,\"logo_url\":null},\"children\":[]},{\"id\":\"d1605792-17ef-44bf-b2a9-42bf42907f5f\",\"publication_id\":1084089,\"sibling_rank\":9999,\"link_title\":null,\"link_url\":null,\"section_id\":327741,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":{\"id\":327741,\"slug\":\"ainews\",\"name\":\"AINews: Weekday Roundups\",\"hide_from_navbar\":false,\"is_podcast\":false,\"logo_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/9a9e98c6-5aeb-461b-b5d0-54d75773e5fa_124x124.png\"},\"children\":[]}],\"contributors\":[{\"name\":\"Latent.Space\",\"handle\":\"swyx\",\"role\":\"admin\",\"owner\":true,\"user_id\":89230629,\"photo_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/db0f8d45-1eb8-4c02-a120-650d377ee52d_640x640.jpeg\",\"bio\":\"Writer, curator, latent space explorer. Main blog: https://swyx.io Devrel/Dev community: https://dx.tips/ Twitter: https://twitter.com/swyx\"}],\"threads_v2_enabled\":false,\"viralGiftsConfig\":{\"id\":\"70ab6904-f65b-4d85-9447-df0494958717\",\"publication_id\":1084089,\"enabled\":false,\"gifts_per_user\":5,\"gift_length_months\":1,\"send_extra_gifts\":true,\"message\":\"The AI Engineer newsletter + Top 10 US Tech podcast. Exploring AI UX, Agents, Devtools, Infra, Open Source Models. See https://latent.space/about for highlights from Chris Lattner, Andrej Karpathy, George Hotz, Simon Willison, Emad Mostaque, et al!\",\"created_at\":\"2024-12-19T21:55:43.55283+00:00\",\"updated_at\":\"2024-12-19T21:55:43.55283+00:00\",\"days_til_invite\":14,\"send_emails\":true,\"show_link\":null},\"tier\":2,\"no_index\":false,\"can_set_google_site_verification\":true,\"can_have_sitemap\":true,\"founding_plan_name_english\":\"Latent Spacenaut\",\"bundles\":[],\"base_url\":\"https://www.latent.space\",\"hostname\":\"www.latent.space\",\"is_on_substack\":false,\"show_links\":[{\"id\":35417,\"publication_id\":1084089,\"section_id\":null,\"url\":\"https://podcasts.apple.com/us/podcast/latent-space-the-ai-engineer-podcast/id1674008350\",\"platform\":\"apple_podcasts\"},{\"id\":27113,\"publication_id\":1084089,\"section_id\":null,\"url\":\"https://open.spotify.com/show/7wd4eyLPJvtWnUK1ugH1oi\",\"platform\":\"spotify\"},{\"id\":27114,\"publication_id\":1084089,\"section_id\":null,\"url\":\"https://open.spotify.com/show/7wd4eyLPJvtWnUK1ugH1oi\",\"platform\":\"spotify_for_paid_users\"}],\"spotify_podcast_settings\":{\"id\":7020,\"publication_id\":1084089,\"section_id\":null,\"spotify_access_token\":\"7b7a1a8a-d456-4883-8107-3b04d028beab\",\"spotify_uri\":\"spotify:show:7wd4eyLPJvtWnUK1ugH1oi\",\"spotify_podcast_title\":null,\"created_at\":\"2024-04-17T14:40:50.766Z\",\"updated_at\":\"2024-04-17T14:42:36.242Z\",\"currently_published_on_spotify\":true,\"feed_url_for_spotify\":\"https://api.substack.com/feed/podcast/spotify/7b7a1a8a-d456-4883-8107-3b04d028beab/1084089.rss\",\"spotify_show_url\":\"https://open.spotify.com/show/7wd4eyLPJvtWnUK1ugH1oi\"},\"podcastPalette\":{\"Vibrant\":{\"rgb\":[204,105,26],\"population\":275},\"DarkVibrant\":{\"rgb\":[127,25,90],\"population\":313},\"LightVibrant\":{\"rgb\":[212,111,247],\"population\":333},\"Muted\":{\"rgb\":[152,69,68],\"population\":53},\"DarkMuted\":{\"rgb\":[50,23,49],\"population\":28},\"LightMuted\":{\"rgb\":[109.71710526315789,8.052631578947365,144.94736842105263],\"population\":0}},\"pageThemes\":{\"podcast\":null},\"multiple_pins\":true,\"live_subscriber_counts\":false,\"supports_ip_content_unlock\":false,\"appTheme\":{\"colors\":{\"accent\":{\"name\":\"#9333ea\",\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":126,\"g\":28,\"b\":214,\"a\":1},\"primary_elevated\":{\"r\":126,\"g\":28,\"b\":214,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"bg_hover\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.3},\"dark\":{\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"primary_elevated\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"bg_hover\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.3}}},\"fg\":{\"primary\":{\"r\":0,\"g\":0,\"b\":0,\"a\":0.8},\"secondary\":{\"r\":0,\"g\":0,\"b\":0,\"a\":0.6},\"tertiary\":{\"r\":0,\"g\":0,\"b\":0,\"a\":0.4},\"accent\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"dark\":{\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.9},\"secondary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.6},\"tertiary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.4},\"accent\":{\"r\":174,\"g\":77,\"b\":255,\"a\":1}}},\"bg\":{\"name\":\"#ffffff\",\"hue\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0},\"tint\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0},\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"primary_hover\":{\"r\":250,\"g\":250,\"b\":250,\"a\":1},\"primary_elevated\":{\"r\":250,\"g\":250,\"b\":250,\"a\":1},\"secondary\":{\"r\":238,\"g\":238,\"b\":238,\"a\":1},\"secondary_elevated\":{\"r\":206.90096477355226,\"g\":206.90096477355175,\"b\":206.9009647735519,\"a\":1},\"tertiary\":{\"r\":219,\"g\":219,\"b\":219,\"a\":1},\"quaternary\":{\"r\":182,\"g\":182,\"b\":182,\"a\":1},\"dark\":{\"primary\":{\"r\":22,\"g\":23,\"b\":24,\"a\":1},\"primary_hover\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"primary_elevated\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"secondary\":{\"r\":35,\"g\":37,\"b\":37,\"a\":1},\"secondary_elevated\":{\"r\":41.35899397549579,\"g\":43.405356429195315,\"b\":43.40489285041963,\"a\":1},\"tertiary\":{\"r\":54,\"g\":55,\"b\":55,\"a\":1},\"quaternary\":{\"r\":90,\"g\":91,\"b\":91,\"a\":1}}}},\"cover_image\":{\"url\":\"https://substackcdn.com/image/fetch/$s_!1PJi!,w_1200,h_400,c_pad,f_auto,q_auto:best,fl_progressive:steep,b_auto:border,b_rgb:ffffff/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa4fe1182-38af-4a5d-bacc-439c36225e87_5000x1200.png\",\"height\":400,\"width\":5000}},\"portalAppTheme\":{\"colors\":{\"accent\":{\"name\":\"#9333ea\",\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":135,\"g\":28,\"b\":232,\"a\":1},\"primary_elevated\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":255,\"g\":103,\"b\":25,\"a\":0.2},\"bg_hover\":{\"r\":255,\"g\":103,\"b\":25,\"a\":0.3},\"dark\":{\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"primary_elevated\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"bg_hover\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.3}}},\"fg\":{\"primary\":{\"r\":54,\"g\":55,\"b\":55,\"a\":1},\"secondary\":{\"r\":134,\"g\":135,\"b\":135,\"a\":1},\"tertiary\":{\"r\":146,\"g\":146,\"b\":146,\"a\":1},\"accent\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"dark\":{\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.9},\"secondary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.6},\"tertiary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.4},\"accent\":{\"r\":174,\"g\":77,\"b\":255,\"a\":1}}},\"bg\":{\"name\":\"#ffffff\",\"hue\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"tint\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"primary_hover\":{\"r\":240,\"g\":240,\"b\":240,\"a\":1},\"primary_elevated\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"secondary\":{\"r\":240,\"g\":240,\"b\":240,\"a\":1},\"secondary_elevated\":{\"r\":240,\"g\":240,\"b\":240,\"a\":1},\"tertiary\":{\"r\":221,\"g\":221,\"b\":221,\"a\":1},\"quaternary\":{\"r\":183,\"g\":183,\"b\":183,\"a\":1},\"dark\":{\"primary\":{\"r\":22,\"g\":23,\"b\":24,\"a\":1},\"primary_hover\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"primary_elevated\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"secondary\":{\"r\":35,\"g\":37,\"b\":37,\"a\":1},\"secondary_elevated\":{\"r\":41.35899397549579,\"g\":43.405356429195315,\"b\":43.40489285041963,\"a\":1},\"tertiary\":{\"r\":54,\"g\":55,\"b\":55,\"a\":1},\"quaternary\":{\"r\":90,\"g\":91,\"b\":91,\"a\":1}}},\"wordmark_bg\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1}},\"fonts\":{\"heading\":\"slab\",\"body\":\"sans\"}},\"logoPalette\":{\"Vibrant\":{\"rgb\":[200,99,28],\"population\":378},\"DarkVibrant\":{\"rgb\":[12,77,99],\"population\":37},\"LightVibrant\":{\"rgb\":[212,110,247],\"population\":348},\"Muted\":{\"rgb\":[152,68,67],\"population\":50},\"DarkMuted\":{\"rgb\":[122,64,142],\"population\":19},\"LightMuted\":{\"rgb\":[109.99999999999996,8,145],\"population\":0}}},\"confirmedLogin\":false,\"hide_intro_popup\":false,\"block_auto_login\":false,\"domainInfo\":{\"isSubstack\":false,\"customDomain\":\"www.latent.space\"},\"experimentFeatures\":{},\"experimentExposures\":{},\"siteConfigs\":{\"score_upsell_email\":\"control\",\"first_chat_email_enabled\":true,\"reader-onboarding-promoted-pub\":737237,\"new_commenter_approval\":false,\"pub_update_opennode_api_key\":false,\"notes_video_max_duration_minutes\":15,\"show_content_label_age_gating_in_feed\":false,\"zendesk_automation_cancellations\":false,\"hide_book_a_meeting_button\":false,\"enable_saved_segments\":false,\"mfa_action_box_enabled\":false,\"publication_max_bylines\":35,\"no_contest_charge_disputes\":false,\"feed_posts_previously_seen_weight\":0.1,\"publication_tabs_reorder\":false,\"comp_expiry_email_new_copy\":\"NONE\",\"free_unlock_required\":false,\"traffic_rule_check_enabled\":false,\"amp_emails_enabled\":false,\"enable_post_summarization\":false,\"live_stream_host_warning_message\":\"\",\"bitcoin_enabled\":false,\"minimum_ios_os_version\":\"17.0.0\",\"show_entire_square_image\":false,\"hide_subscriber_count\":false,\"fit_in_live_stream_player\":false,\"publication_author_display_override\":\"\",\"ios_webview_payments_enabled\":\"control\",\"generate_pdf_tax_report\":false,\"show_generic_post_importer\":false,\"enable_pledges_modal\":true,\"include_pdf_invoice\":false,\"enable_callout_block\":false,\"notes_weight_watch_video\":5,\"enable_react_dashboard\":false,\"meetings_v1\":false,\"enable_videos_page\":false,\"exempt_from_gtm_filter\":false,\"group_sections_and_podcasts_in_menu\":false,\"boost_optin_modal_enabled\":true,\"standards_and_enforcement_features_enabled\":false,\"pub_creation_captcha_behavior\":\"risky_pubs_or_rate_limit\",\"post_blogspot_importer\":false,\"notes_weight_short_item_boost\":0.15,\"enable_high_res_background_uploading\":false,\"pub_tts_override\":\"default\",\"disable_monthly_subscriptions\":false,\"skip_welcome_email\":false,\"chat_reader_thread_notification_default\":false,\"scheduled_pinned_posts\":false,\"disable_redirect_outbound_utm_params\":false,\"reader_gift_referrals_enabled\":true,\"dont_show_guest_byline\":false,\"like_comments_enabled\":true,\"enable_grouped_library\":false,\"temporal_livestream_ended_draft\":true,\"enable_author_note_email_toggle\":false,\"meetings_embed_publication_name\":false,\"fallback_to_archive_search_on_section_pages\":false,\"livekit_track_egress_custom_base_url\":\"http://livekit-egress-custom-recorder-participant-test.s3-website-us-east-1.amazonaws.com\",\"people_you_may_know_algorithm\":\"experiment\",\"welcome_screen_blurb_override\":\"\",\"notes_weight_low_impression_boost\":0.3,\"like_posts_enabled\":true,\"feed_promoted_video_boost\":1.5,\"twitter_player_card_enabled\":true,\"subscribe_bypass_preact_router\":false,\"feed_promoted_user\":false,\"show_note_stats_for_all_notes\":false,\"section_specific_csv_imports_enabled\":false,\"disable_podcast_feed_description_cta\":false,\"bypass_profile_substack_logo_detection\":false,\"use_preloaded_player_sources\":false,\"enable_tiktok_oauth\":false,\"list_pruning_enabled\":false,\"facebook_connect\":false,\"opt_in_to_sections_during_subscribe\":false,\"dpn_weight_share\":2,\"underlined_colored_links\":false,\"enable_efficient_digest_embed\":false,\"extract_stripe_receipt_url\":false,\"enable_aligned_images\":false,\"max_image_upload_mb\":64,\"threads_suggested_ios_version\":null,\"pledges_disabled\":false,\"threads_minimum_ios_version\":812,\"hide_podcast_email_setup_link\":false,\"subscribe_captcha_behavior\":\"default\",\"publication_ban_sample_rate\":0,\"enable_note_polls\":false,\"ios_enable_publication_activity_tab\":false,\"custom_themes_substack_subscribe_modal\":false,\"ios_post_share_assets_screenshot_trigger\":\"control\",\"opt_in_to_sections_during_subscribe_include_main_pub_newsletter\":false,\"continue_support_cta_in_newsletter_emails\":false,\"bloomberg_syndication_enabled\":false,\"welcome_page_app_button\":true,\"lists_enabled\":false,\"adhoc_email_batch_delay_ms\":0,\"generated_database_maintenance_mode\":false,\"allow_document_freeze\":false,\"test_age_gate_user\":false,\"podcast_main_feed_is_firehose\":false,\"pub_app_incentive_gift\":\"\",\"no_embed_redirect\":false,\"customized_email_from_name_for_new_follow_emails\":\"treatment\",\"spotify_open_access_sandbox_mode\":false,\"enable_founding_iap_plans\":true,\"fullstory_enabled\":false,\"chat_reply_poll_interval\":3,\"dpn_weight_follow_or_subscribe\":3,\"thefp_enable_email_upsell_banner\":false,\"android_restore_feed_scroll_position\":\"experiment\",\"force_pub_links_to_use_subdomain\":false,\"always_show_cookie_banner\":false,\"hide_media_download_option\":false,\"hide_post_restacks\":false,\"feed_item_source_debug_mode\":false,\"ios_subscription_bar_live_polling_enabled\":true,\"enable_user_status_ui\":false,\"publication_homepage_title_display_override\":\"\",\"post_preview_highlight_byline\":false,\"4k_video\":false,\"enable_islands_section_intent_screen\":false,\"post_metering_enabled\":false,\"notifications_disabled\":\"\",\"cross_post_notification_threshold\":1000,\"facebook_connect_prod_app\":true,\"force_into_pymk_ranking\":false,\"minimum_android_version\":756,\"live_stream_krisp_noise_suppression_enabled\":false,\"enable_transcription_translations\":false,\"nav_group_items\":false,\"use_og_image_as_twitter_image_for_post_previews\":false,\"always_use_podcast_channel_art_as_episode_art_in_rss\":false,\"enable_sponsorship_perks\":false,\"seo_tier_override\":\"NONE\",\"editor_role_enabled\":false,\"no_follow_links\":false,\"publisher_api_enabled\":false,\"zendesk_support_priority\":\"default\",\"enable_post_clips_stats\":false,\"enable_subscriber_referrals_awards\":true,\"ios_profile_themes_feed_permalink_enabled\":false,\"include_thumbnail_landscape_layouts\":true,\"use_publication_language_for_transcription\":false,\"show_substack_funded_gifts_tooltip\":true,\"disable_ai_transcription\":false,\"thread_permalink_preview_min_ios_version\":4192,\"live_stream_founding_audience_enabled\":false,\"android_toggle_on_website_enabled\":false,\"internal_android_enable_post_editor\":false,\"enable_pencraft_sandbox_access\":false,\"updated_inbox_ui\":false,\"live_stream_creation_enabled\":true,\"disable_card_element_in_europe\":false,\"web_growth_item_promotion_threshold\":0,\"bundle_subscribe_enabled\":false,\"enable_web_typing_indicators\":false,\"web_vitals_sample_rate\":0,\"allow_live_stream_auto_takedown\":\"true\",\"mobile_publication_attachments_enabled\":false,\"ios_post_dynamic_title_size\":false,\"ios_enable_live_stream_highlight_trailer_toggle\":false,\"ai_image_generation_enabled\":true,\"disable_personal_substack_initialization\":false,\"section_specific_welcome_pages\":false,\"local_payment_methods\":\"control\",\"publisher_api_cancel_comp\":false,\"posts_in_rss_feed\":20,\"post_rec_endpoint\":\"\",\"publisher_dashboard_section_selector\":false,\"reader_surveys_platform_question_order\":\"36,1,4,2,3,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35\",\"developer_api_enabled\":false,\"login_guard_app_link_in_email\":true,\"community_moderators_enabled\":false,\"monthly_sub_is_one_off\":false,\"unread_notes_activity_digest\":\"control\",\"display_cookie_settings\":false,\"welcome_page_query_params\":false,\"enable_free_podcast_urls\":false,\"email_post_stats_v2\":false,\"comp_expiry_emails_disabled\":false,\"enable_description_on_polls\":false,\"use_microlink_for_instagram_embeds\":false,\"post_notification_batch_delay_ms\":30000,\"free_signup_confirmation_behavior\":\"with_email_validation\",\"ios_post_stats_for_admins\":false,\"enable_livestream_branding\":true,\"use_livestream_post_media_composition\":true,\"section_specific_preambles\":false,\"pub_export_temp_disable\":false,\"show_menu_on_posts\":false,\"android_reset_backstack_after_timeout\":false,\"ios_post_subscribe_web_routing\":true,\"ios_writer_stats_public_launch_v2\":false,\"min_size_for_phishing_check\":1,\"enable_android_post_stats\":false,\"ios_chat_revamp_enabled\":false,\"app_onboarding_survey_email\":false,\"republishing_enabled\":false,\"app_mode\":false,\"show_phone_banner\":true,\"live_stream_video_enhancer\":\"internal\",\"minimum_ios_version\":2200,\"enable_author_pages\":false,\"enable_decagon_chat\":true,\"first_month_upsell\":\"control\",\"enable_subscriber_tags\":false,\"new_user_checklist_enabled\":\"use_follower_count\",\"ios_feed_note_status_polling_enabled\":false,\"latex_upgraded_inline\":false,\"show_attached_profile_for_pub_setting\":false,\"ios_feed_subscribe_upsell\":\"experiment\",\"rss_verification_code\":\"\",\"notification_post_emails\":\"experiment\",\"notes_weight_follow\":3.8,\"chat_suppress_contributor_push_option_enabled\":false,\"use_og_image_asset_variant\":\"\",\"export_hooks_enabled\":false,\"audio_encoding_bitrate\":null,\"bestseller_pub_override\":false,\"extra_seats_coupon_type\":false,\"post_subdomain_universal_links\":false,\"post_import_max_file_size\":26214400,\"feed_promoted_video_publication\":false,\"livekit_reconnect_slate_url\":\"https://mux-livestream-assets.s3.us-east-1.amazonaws.com/custom-disconnect-slate-tall.png\",\"exclude_from_pymk_suggestions\":false,\"publication_ranking_variant\":\"experiment\",\"disable_annual_subscriptions\":false,\"hack_jane_manchun_wong\":true,\"android_enable_auto_gain_control\":true,\"enable_android_dms\":false,\"allow_coupons_on_upgrade\":false,\"test_au_age_gate_user\":false,\"pub_auto_moderation_enabled\":false,\"disable_live_stream_ai_trimming_by_default\":false,\"disable_deletion\":false,\"ios_default_coupon_enabled\":false,\"notes_weight_read_post\":5,\"notes_weight_reply\":3,\"livekit_egress_custom_base_url\":\"http://livekit-egress-custom-recorder.s3-website-us-east-1.amazonaws.com\",\"clip_focused_video_upload_flow\":false,\"live_stream_max_guest_users\":2,\"android_upgrade_alert_dialog_reincarnated\":true,\"enable_video_seo_data\":false,\"can_reimport_unsubscribed_users_with_2x_optin\":false,\"feed_posts_weight_subscribed\":0,\"founding_upgrade_during_gift_disabled\":false,\"live_event_mixin\":\"\",\"review_incoming_email\":\"default\",\"media_feed_subscribed_posts_weight\":0.5,\"enable_founding_gifts\":false,\"enable_creator_agency_pages\":false,\"enable_sponsorship_campaigns\":false,\"thread_permalink_preview_min_android_version\":2037,\"enable_creator_earnings\":true,\"thefp_enable_embed_media_links\":false,\"thumbnail_selection_max_frames\":300,\"sort_modal_search_results\":false,\"default_thumbnail_time\":10,\"pub_ranking_weight_retained_engagement\":1,\"load_test_unichat\":false,\"notes_read_post_baseline\":0,\"live_stream_head_alignment_guide\":false,\"show_open_post_as_pdf_button\":false,\"free_press_combo_subscribe_flow_enabled\":false,\"android_note_auto_share_assets\":\"control\",\"pub_ranking_weight_immediate_engagement\":0.5,\"enable_portal_feed_post_comments\":false,\"gifts_from_substack_feature_available\":true,\"disable_ai_clips\":false,\"enable_elevenlabs_voiceovers\":false,\"use_web_livestream_thumbnail_editor\":true,\"show_simple_post_editor\":false,\"instacart_integration_enabled\":false,\"enable_publication_podcasts_page\":false,\"android_profile_share_assets_experiment\":\"treatment\",\"use_advanced_fonts\":false,\"growth_sources_all_time\":true,\"ios_note_composer_settings_enabled\":false,\"android_v2_post_video_player_enabled\":false,\"enable_direct_message_request_bypass\":false,\"enable_apple_news_sync\":false,\"live_stream_in_trending_topic_overrides\":\"\",\"media_feed_prepend_inbox_limit\":30,\"free_press_newsletter_promo_enabled\":false,\"enable_ios_livestream_stats\":true,\"disable_live_stream_reactions\":false,\"feed_posts_weight_negative\":2.5,\"instacart_partner_id\":\"\",\"clip_generation_3rd_party_vendor\":\"internal\",\"ios_onboarding_collapsable_categories_with_sentiment\":\"experiment\",\"welcome_page_no_opt_out\":false,\"android_feed_menu_copy_link_experiment\":\"experiment\",\"notes_weight_negative\":1,\"ios_discover_tab_min_installed_date\":\"2025-06-09T16:56:58+0000\",\"notes_weight_click_see_more\":2,\"edit_profile_theme_colors\":false,\"notes_weight_like\":2.4,\"disable_clipping_for_readers\":false,\"android_creator_earnings_enabled\":true,\"feed_posts_weight_reply\":3,\"feed_posts_weight_like\":1.5,\"feed_posts_weight_share\":3,\"feed_posts_weight_save\":3,\"enable_press_kit_preview_modal\":false,\"dpn_weight_tap_clickbait_penalty\":0.5,\"feed_posts_weight_sign_up\":4,\"live_stream_video_degradation_preference\":\"maintainFramerate\",\"enable_high_follower_dm\":true,\"pause_app_badges\":false,\"android_enable_publication_activity_tab\":false,\"ios_hide_author_in_share_sheet\":\"control\",\"profile_feed_expanded_inventory\":false,\"phone_verification_fallback_to_twilio\":false,\"android_onboarding_suggestions_hero_text\":\"experiment\",\"livekit_mux_latency_mode\":\"low\",\"feed_juiced_user\":0,\"universal_feed_translator_experiment\":\"control\",\"notes_click_see_more_baseline\":0.35,\"enable_polymarket_expandable_embeds\":true,\"publication_onboarding_weight_std_dev\":0,\"can_see_fast_subscriber_counts\":true,\"android_enable_user_status_ui\":false,\"use_advanced_commerce_api_for_iap\":false,\"skip_free_preview_language_in_podcast_notes\":false,\"larger_wordmark_on_publication_homepage\":false,\"video_editor_full_screen\":false,\"enable_mobile_stats_for_admins\":false,\"ios_profile_themes_note_composer_enabled\":false,\"enable_persona_sandbox_environment\":false,\"notes_weight_click_item\":3,\"notes_weight_long_visit\":1,\"bypass_single_unlock_token_limit\":false,\"notes_watch_video_baseline\":0.08,\"enable_free_trial_subscription_ios\":true,\"polymarket_minimum_confidence_for_trending_topics\":100,\"add_section_and_tag_metadata\":false,\"daily_promoted_notes_enabled\":true,\"enable_islands_cms\":false,\"enable_livestream_combined_stats\":false,\"ios_social_subgroups_enabled\":false,\"chartbeat_video_enabled\":false,\"enable_drip_campaigns\":false,\"adhoc_email_batch_size\":5000,\"ios_offline_mode_enabled\":false,\"enable_pinned_portals\":false,\"post_management_search_engine\":\"elasticsearch\",\"new_bestseller_leaderboard_feed_item_enabled\":false,\"feed_main_disabled\":false,\"enable_account_settings_revamp\":false,\"allowed_email_domains\":\"one\",\"thefp_enable_fp_recirc_block\":false,\"top_search_variant\":\"control\",\"enable_debug_logs_ios\":false,\"show_pub_content_on_profile_for_pub_id\":0,\"show_pub_content_on_profile\":false,\"livekit_track_egress\":true,\"video_tab_mixture_pattern\":\"npnnnn\",\"enable_theme_contexts\":false,\"onboarding_suggestions_search\":\"experiment\",\"feed_tuner_enabled\":false,\"livekit_mux_latency_mode_rtmp\":\"low\",\"draft_notes_enabled\":true,\"fcm_high_priority\":false,\"enable_drop_caps\":true,\"search_category_variant\":\"control\",\"highlighted_code_block_enabled\":true,\"dpn_weight_tap_bonus_subscribed\":0,\"iap_announcement_blog_url\":\"\",\"android_onboarding_progress_persistence\":\"control\",\"ios_livestream_feedback\":false,\"founding_plan_upgrade_warning\":false,\"dpn_weight_like\":3,\"dpn_weight_short_session\":1,\"ios_enable_custom_thumbnail_generation\":true,\"ios_mediaplayer_reply_bar_v2\":false,\"android_view_post_share_assets_employees_only\":false,\"stripe_link_in_payment_element_v3\":\"treatment\",\"enable_notification_email_batching\":true,\"notes_weight_follow_boost\":10,\"profile_portal_theme\":false,\"ios_hide_portal_tab_bar\":false,\"follow_upsell_rollout_percentage\":30,\"android_activity_item_sharing_experiment\":\"control\",\"live_stream_invite_ttl_seconds\":900000,\"include_founding_plans_coupon_option\":false,\"thefp_enable_cancellation_discount_offer\":false,\"dpn_weight_reply\":2,\"thefp_free_trial_experiment\":\"treatment\",\"android_enable_edit_profile_theme\":false,\"twitter_api_enabled\":true,\"dpn_weight_follow\":3,\"thumbnail_selection_engine\":\"openai\",\"enable_adhoc_email_batching\":0,\"notes_weight_author_low_impression_boost\":0.2,\"disable_audio_enhancement\":false,\"pub_search_variant\":\"control\",\"ignore_video_in_notes_length_limit\":false,\"web_show_scores_on_sports_tab\":false,\"notes_weight_click_share\":3,\"allow_long_videos\":true,\"feed_posts_weight_long_click\":15,\"dpn_score_threshold\":0,\"thefp_annual_subscription_promotion\":\"treatment\",\"dpn_weight_follow_bonus\":0.5,\"use_intro_clip_and_branded_intro_by_default\":false,\"use_enhanced_video_embed_player\":true,\"community_profile_activity_feed\":false,\"android_reader_share_assets_3\":\"control\",\"email_change_minimum_bot_score\":0,\"mobile_age_verification_learn_more_link\":\"https://on.substack.com/p/our-position-on-the-online-safety\",\"enable_viewing_all_livestream_viewers\":false,\"web_suggested_search_route_recent_search\":\"control\",\"enable_clip_prompt_variant_filtering\":true,\"chartbeat_enabled\":false,\"dpn_weight_disable\":10,\"dpn_ranking_enabled\":true,\"reply_flags_enabled\":true,\"enable_custom_email_css\":false,\"dpn_model_variant\":\"experiment\",\"android_og_tag_post_sharing_experiment\":\"control\",\"platform_search_variant\":\"control\",\"enable_apple_podcast_auto_publish\":false,\"linkedin_profile_search_enabled\":false,\"ios_better_top_search_prompt_in_global_search\":\"control\",\"retire_i18n_marketing_pages\":true,\"publication_has_own_app\":false,\"suggested_minimum_ios_version\":0,\"dpn_weight_open\":2.5,\"ios_pogs_stories\":\"experiment\",\"enable_notes_admins\":false,\"trending_topics_module_long_term_experiment\":\"control\",\"enable_suggested_searches\":true,\"enable_subscription_notification_email_batching\":true,\"android_synchronous_push_notif_handling\":\"control\",\"thumbnail_selection_skip_desktop_streams\":false,\"a24_redemption_link\":\"\",\"dpn_weight_tap\":2.5,\"ios_live_stream_auto_gain_enabled\":true,\"dpn_weight_restack\":2,\"dpn_weight_negative\":40,\"enable_publication_tts_player\":false,\"enable_ios_post_page_themes\":false,\"session_version_invalidation_enabled\":false,\"search_retrieval_variant\":\"experiment\",\"galleried_feed_attachments\":true,\"web_post_attachment_fallback\":\"treatment\",\"enable_live_stream_thumbnail_treatment_validation\":true,\"forced_featured_topic_id\":\"\",\"ios_audio_captions_disabled\":false,\"reader_onboarding_modal_v2_vs_page\":\"experiment\",\"related_posts_enabled\":false,\"use_progressive_editor_rollout\":true,\"ios_live_stream_pip_dismiss_v4\":\"control\",\"reply_rate_limit_max_distinct_users_daily\":110,\"galleried_feed_attachments_in_composer\":false,\"android_rank_share_destinations_experiment\":\"control\",\"publisher_banner\":\"\",\"suggested_search_metadata_web_ui\":true,\"mobile_user_attachments_enabled\":false,\"enable_library_compaction\":true,\"ios_founding_upgrade_button_in_portals_v2\":\"control\",\"enable_ios_chat_themes\":false,\"feed_weight_language_mismatch_penalty\":0.6,\"default_orange_quote_experiment\":\"control\",\"enable_high_res_recording_workflow\":false,\"community_activity_feed_author_to_community_content_ratio\":0.5,\"enable_sponsorship_profile\":false,\"ios_onboarding_multiple_notification_asks\":\"control\",\"ios_founding_upgrade_button_in_portals\":\"control\",\"ios_mid_read_post_reminder_v2\":\"treatment\",\"ios_inline_upgrade_on_feed_items\":\"control\",\"reply_rate_limit_max_distinct_users_monthly\":600,\"show_branded_intro_setting\":false,\"desktop_live_stream_screen_share_audio_enabled\":false,\"search_posts_use_top_search\":false,\"ios_inbox_observe_by_key\":true,\"profile_photo_upsell_modal\":\"treatment\",\"enable_high_res_background_uploading_session_recovery\":false,\"portal_post_style\":\"control\",\"search_ranker_variant\":\"experiment\",\"dpn_weight_long_session\":2,\"use_custom_header_by_default\":false,\"ios_listen_tab\":false,\"android_composer_modes_vs_attachments\":\"control\",\"activity_item_ranking_variant\":\"experiment\",\"android_polymarket_embed_search\":false,\"ios_onboarding_new_user_survey\":\"experiment\",\"android_post_like_share_nudge\":\"treatment\",\"android_post_bottom_share_experiment\":\"treatment\",\"enable_post_templates\":true,\"use_thumbnail_selection_sentiment_matching\":true,\"skip_adhoc_email_sends\":false,\"android_enable_draft_notes\":true,\"permalink_reply_ranking_variant\":\"experiment\",\"desktop_live_stream_participant_labels\":false,\"allow_feed_category_filtering\":false,\"enable_livestream_screenshare_detection\":true,\"private_live_streaming_enabled\":true,\"android_scheduled_notes_enabled\":true,\"private_live_streaming_banner_enabled\":false,\"portal_ranking_variant\":\"experiment\",\"desktop_live_stream_safe_framing\":0.8,\"android_onboarding_swipeable_cards\":\"control\",\"enable_note_scheduling\":true,\"ios_limit_related_notes_in_permalink\":\"control\"},\"publicationSettings\":{\"block_ai_crawlers\":false,\"credit_token_enabled\":true,\"custom_tos_and_privacy\":false,\"did_identity\":\"did:plc:es3srknleppmlecmx45g2hoe\",\"disable_optimistic_bank_payments\":false,\"display_welcome_page_details\":true,\"enable_meetings\":false,\"payment_pledges_enabled\":true,\"enable_drop_caps\":false,\"enable_post_page_conversion\":false,\"enable_prev_next_nav\":true,\"enable_restacking\":true,\"gifts_from_substack_disabled\":false,\"google_analytics_4_token\":null,\"group_sections_and_podcasts_in_menu_enabled\":false,\"live_stream_homepage_visibility\":\"contributorsAndAdmins\",\"live_stream_homepage_style\":\"banner\",\"medium_length_description\":\"The AI Engineer newsletter + Top 10 US Tech podcast + Community. Interviews, Essays and Guides on frontier LLMs, AI Infra, Agents, Devtools, UX, Open Models. See https://latent.space/about for highlights from Chris Lattner, Andrej Karpathy, George Hotz, Simon Willison, Soumith Chintala, et al!\",\"notes_feed_enabled\":false,\"paywall_unlock_tokens\":false,\"post_preview_crop_gravity\":\"auto\",\"post_preview_radius\":\"xs\",\"reader_referrals_enabled\":true,\"reader_referrals_leaderboard_enabled\":true,\"seen_coming_soon_explainer\":false,\"seen_google_analytics_migration_modal\":false,\"local_currency_modal_seen\":true,\"local_payment_methods_modal_seen\":true,\"twitter_pixel_signup_event_id\":null,\"twitter_pixel_subscribe_event_id\":null,\"use_local_currency\":true,\"welcome_page_opt_out_text\":\"No thanks\",\"cookie_settings\":\"\",\"show_restacks_below_posts\":true,\"holiday_gifting_post_header\":true,\"homepage_message_text\":\"\",\"homepage_message_link\":\"\",\"about_us_author_ids\":\"\",\"archived_section_ids\":\"\",\"column_section_ids\":\"\",\"fp_primary_column_section_ids\":\"\",\"event_section_ids\":\"\",\"podcasts_metadata\":\"\",\"video_section_ids\":\"\",\"post_metering_enabled\":false},\"publicationUserSettings\":null,\"userSettings\":{\"user_id\":null,\"activity_likes_enabled\":true,\"dashboard_nav_refresh_enabled\":false,\"hasDismissedSectionToNewsletterRename\":false,\"is_guest_post_enabled\":true,\"feed_web_nux_seen_at\":null,\"has_seen_select_to_restack_tooltip_nux\":false,\"invite_friends_nux_dismissed_at\":null,\"suggestions_feed_item_last_shown_at\":null,\"has_seen_select_to_restack_modal\":false,\"last_notification_alert_shown_at\":null,\"disable_reply_hiding\":false,\"newest_seen_chat_item_published_at\":null,\"explicitContentEnabled\":false,\"contactMatchingEnabled\":false,\"messageRequestLevel\":\"everyone\",\"liveStreamAcceptableInviteLevel\":\"everyone\",\"liveStreamAcceptableChatLevel\":\"everyone\",\"creditTokensTreatmentExposed\":false,\"appBadgeIncludesChat\":false,\"autoPlayVideo\":true,\"smart_delivery_enabled\":false,\"chatbotTermsLastAcceptedAt\":null,\"has_seen_notes_post_app_upsell\":false,\"substack_summer_nux_dismissed_at\":null,\"first_note_id\":null,\"show_concurrent_live_stream_viewers\":false,\"has_dismissed_fp_download_pdf_nux\":false,\"edit_profile_feed_item_dismissed_at\":null,\"mobile_permalink_app_upsell_seen_at\":null,\"new_user_checklist_enabled\":false,\"new_user_follow_subscribe_prompt_dismissed_at\":null,\"has_seen_youtube_shorts_auto_publish_announcement\":false,\"has_seen_publish_youtube_connect_upsell\":false,\"notificationQualityFilterEnabled\":true,\"hasSeenOnboardingNewslettersScreen\":false,\"bestsellerBadgeEnabled\":true,\"hasSelfIdentifiedAsCreator\":false,\"autoTranslateEnabled\":true,\"autoTranslateBlocklist\":[]},\"subscriberCountDetails\":\"hundreds of thousands of subscribers\",\"mux_env_key\":\"u42pci814i6011qg3segrcpp9\",\"persona_environment_id\":\"env_o1Lbk4JhpY4PmvNkwaBdYwe5Fzkt\",\"sentry_environment\":\"production\",\"launchWelcomePage\":false,\"pendingInviteForActiveLiveStream\":null,\"isEligibleForLiveStreamCreation\":true,\"webviewPlatform\":null,\"noIndex\":false,\"post\":{\"audience\":\"everyone\",\"audience_before_archived\":null,\"canonical_url\":\"https://www.latent.space/p/felix-anthropic\",\"default_comment_sort\":null,\"editor_v2\":false,\"exempt_from_archive_paywall\":false,\"free_unlock_required\":false,\"id\":191097767,\"podcast_art_url\":null,\"podcast_duration\":5219.265,\"podcast_preview_upload_id\":null,\"podcast_upload_id\":\"ec442b0a-bce1-438e-9940-0c654aaede15\",\"podcast_url\":\"https://api.substack.com/api/v1/audio/upload/ec442b0a-bce1-438e-9940-0c654aaede15/src\",\"post_date\":\"2026-03-17T21:39:16.758Z\",\"updated_at\":\"2026-03-17T21:39:17.044Z\",\"publication_id\":1084089,\"search_engine_description\":null,\"search_engine_title\":null,\"section_id\":null,\"should_send_free_preview\":false,\"show_guest_bios\":true,\"slug\":\"felix-anthropic\",\"social_title\":null,\"subtitle\":\"\",\"teaser_post_eligible\":true,\"title\":\"Why Anthropic Thinks AI Should Have Its Own Computer \u2014 Felix Rieseberg of Claude Cowork & Claude Code Desktop\",\"type\":\"podcast\",\"video_upload_id\":null,\"write_comment_permissions\":\"everyone\",\"meter_type\":\"none\",\"live_stream_id\":null,\"is_published\":true,\"restacks\":4,\"reactions\":{\"\u2764\":33},\"top_exclusions\":[],\"pins\":[],\"section_pins\":[],\"has_shareable_clips\":false,\"previous_post_slug\":\"turbopuffer\",\"next_post_slug\":\"dreamer\",\"cover_image\":\"https://substack-video.s3.amazonaws.com/video_upload/post/191097767/ec442b0a-bce1-438e-9940-0c654aaede15/transcoded-1773778585.png\",\"cover_image_is_square\":false,\"cover_image_is_explicit\":false,\"podcast_episode_image_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/534f41b9-5d2b-49b9-9578-4852473c362f_1400x1400.png\",\"podcast_episode_image_info\":{\"url\":\"https://substack-post-media.s3.amazonaws.com/public/images/534f41b9-5d2b-49b9-9578-4852473c362f_1400x1400.png\",\"isDefaultArt\":false,\"isDefault\":false},\"videoUpload\":null,\"podcastFields\":{\"post_id\":191097767,\"podcast_episode_number\":null,\"podcast_season_number\":null,\"podcast_episode_type\":null,\"should_syndicate_to_other_feed\":null,\"syndicate_to_section_id\":null,\"hide_from_feed\":false,\"free_podcast_url\":null,\"free_podcast_duration\":null},\"podcastUpload\":{\"id\":\"ec442b0a-bce1-438e-9940-0c654aaede15\",\"name\":\"final-felix-audio.mp3\",\"created_at\":\"2026-03-17T20:11:59.999Z\",\"uploaded_at\":\"2026-03-17T20:14:26.465Z\",\"publication_id\":1084089,\"state\":\"transcoded\",\"post_id\":191097767,\"user_id\":46786399,\"duration\":5219.265,\"height\":null,\"width\":null,\"thumbnail_id\":1773778585,\"preview_start\":null,\"preview_duration\":null,\"media_type\":\"audio\",\"primary_file_size\":83508706,\"is_mux\":false,\"mux_asset_id\":null,\"mux_playback_id\":null,\"mux_preview_asset_id\":null,\"mux_preview_playback_id\":null,\"mux_rendition_quality\":null,\"mux_preview_rendition_quality\":null,\"explicit\":false,\"copyright_infringement\":null,\"src_media_upload_id\":null,\"live_stream_id\":null,\"transcription\":{\"media_upload_id\":\"ec442b0a-bce1-438e-9940-0c654aaede15\",\"created_at\":\"2026-03-17T20:15:58.859Z\",\"requested_by\":46786399,\"status\":\"transcribed\",\"modal_call_id\":\"fc-01KKYQ1QQWY9GR4HHDX4WHDTTB\",\"approved_at\":\"2026-03-17T20:21:58.392Z\",\"transcript_url\":\"s3://substack-video/video_upload/post/191097767/ec442b0a-bce1-438e-9940-0c654aaede15/1773778572/transcription.json\",\"attention_vocab\":null,\"speaker_map\":null,\"captions_map\":{\"en\":{\"url\":\"s3://substack-video/video_upload/post/191097767/ec442b0a-bce1-438e-9940-0c654aaede15/1773778572/en.vtt\",\"language\":\"en\",\"original\":true}},\"cdn_url\":\"https://substackcdn.com/video_upload/post/191097767/ec442b0a-bce1-438e-9940-0c654aaede15/1773778572/transcription.json?Expires=1775491872&Key-Pair-Id=APKAIVDA3NPSMPSPESQQ&Signature=gpIT500gOPMqJ~0rkJxqMAeWCqojGh4r5EAosF0gXk2RmPcILikVyaG1qjs4~n-q1pxntUOSRXWDZE8lsi0cH2yW-qcx7qc4-HVbvQBy-zWx5hS7VaCy0GeUHD5PHdr6E59whV5BYiowidS0qrni2eT4p7pQpm2BdosYw0lu1fEC9kDz9wXaGK3Yiq904dJckdEdKGyiUFK7QWAbBCeF3GbcUfcX5on8DsZUUoGzcE9bCUZ8LJ10Dudcd2IdnxIMiIVRxUhIEexGvwGGbGe6M46VmgMnA0vsfgIi4IOw77s6t8DMmj94lBFYUlxpjzF3h8tHCCHenra~0Rortt3Qhw__\",\"cdn_unaligned_url\":\"https://substackcdn.com/video_upload/post/191097767/ec442b0a-bce1-438e-9940-0c654aaede15/1773778572/unaligned_transcription.json?Expires=1775491872&Key-Pair-Id=APKAIVDA3NPSMPSPESQQ&Signature=bOzeefreL-auK~WY7rW2S6gvGHWBBv5Zu6y-wyRPkTSLSprA1anWzLKhiIYqzqG~bo0X6zA5zn6mSAQ0AHGgHoO2buOyAb6kRwONne3WB8eX4VG~Y-iVUTPaRpmxdA~0GanoE4hj-tR-k1B0LH76MBBC37OBK0SZCRxHdWsihc2XNzgtvv7W1roPSHsKv-~wWm0TxYEf4hoJ42XFryOY0-Ifn9l2kYhE5HaiqVxcIoBufW0EmfpLrbOrCIYB8bijXNHwg09Lnqik~Fq6IfVRrhzMubvihciz0RKqfmwxdrXxORNeKE-zmqYU~dqYHa5bQf5OT8Ibw000cobEbqC9mA__\",\"signed_captions\":[{\"language\":\"en\",\"url\":\"https://substackcdn.com/video_upload/post/191097767/ec442b0a-bce1-438e-9940-0c654aaede15/1773778572/en.vtt?Expires=1775491872&Key-Pair-Id=APKAIVDA3NPSMPSPESQQ&Signature=M-AAbK1aj~vShNr0MJjdCNxhHsmFcwkO8Zw8v2eJ8vkv6C6hyV6vIVAIr7jYRtgBIEF~zr2OD3k1lmTbgzwHN6RE~gs8W8b3h209zjkCOS-Psc-DwrM6dvt8FFs4~KHnloeEzi5gIW1Kp5P~6zdI-mG-7df84g8kcPJMsRg7d2BSU951RKjiwrTD9TTmCtliZ5tML4v5hKYLOsCItCPabdP4G~7H4Rb3EzcxMhLi5wsyIiACkvQ4XdlsJuE7RCtwrDdVH0oN5BBWnxExzUm~dmG3va77s1pn3rB13F3bHOZj2rsiFf9cdSKQme0kgRAT~RRu-hbas2qgoHKVXcU52w__\",\"original\":true}]}},\"podcastPreviewUpload\":null,\"voiceover_upload_id\":null,\"voiceoverUpload\":null,\"has_voiceover\":false,\"description\":\"Claude Cowork came out of an accident.\",\"body_html\":\"
Claude Cowork came out of an accident.

Felix and the Anthropic team noticed something interesting with Claude Code: many users were using it primarily for all kinds of messy knowledge work instead of coding. Even technical builders would use it for lots of non-technical work.

Even more shocking, Claude cowork wrote itself. With a team of humans simply orchestrating multiple claude code instances, the tool was ready after a brief week and a half.

This isn\u2019t Felix\u2019s first rodeo with impactful and playful desktop apps. He\u2019s helped ship the Slack desktop app and is a core maintainer of Electron the open-source software framework used for building cross-platform desktop applications, even putting Windows 95 into an Electron app that runs on macOS, Windows, and Linux.
github.com/felixrieseberg\u2026 ","username":"felixrieseberg","name":"Felix Rieseberg","profile_image_url":"https://pbs.substack.com/profile_images/1544558915819487233/qMrauBqx_normal.jpg","date":"2018-08-23T14:54:03.000Z","photos":[{"img_url":"https://pbs.substack.com/media/DlSuLBJVsAAFs8r.jpg","link_url":"https://t.co/YquOnOGrSz"}],"quoted_tweet":{},"reply_count":474,"retweet_count":5615,"like_count":16045,"impression_count":0,"expanded_url":null,"video_url":null,"belowTheFold":false}\\\" data-component-name=\\\"Twitter2ToDOM\\\">
In this episode, Felix joins us to unpack why execution has suddenly become cheap enough that teams can \u201Cjust build all the candidates\u201D and why the real frontier in AI products is no longer better chat, but trusted task execution.

He also shares why Anthropic is betting on local-first agent workflows, why skills may matter more than most people realize, and how the hardest questions ahead are about autonomy, safety, portability, and the changing shape of knowledge work itself.

## We discuss

Felix\u2019s path: Slack desktop app, Electron, Windows 95 in JavaScript, and now building Claude Cowork at Anthropic

What Claude Cowork actually is: a more user-friendly, VM-based version of Claude Code designed to bring agentic workflows to non-terminal-native users

https://news.ycombinator.com/item?id=47220118

Why \u201Cuser-friendly\u201D does not mean \u201Cless powerful\u201D: Cowork as a superset product, much like how VS Code initially looked simpler than Visual Studio but became more hackable and extensible

Anthropic\u2019s prototype-first culture: why Cowork was built in 10 days using many pre-existing internal pieces, and how internal prototypes shaped the final product

Why execution is getting cheap: the shift from long memos, specs, and debate toward rapidly building multiple candidates and choosing based on reality instead of theory

The local debate: why Felix thinks Silicon Valley is undervaluing the local computer, and why putting Claude \u201Cwhere you work\u201D is often more powerful

Why Claude gets its own computer: the VM as both a safety boundary and a capability unlock, letting Claude install tools, run scripts, and work more independently without constant approval

Safety through sandboxing: why \u201Capprove every command\u201D is not a real long-term UX, and how virtual machines create a middle ground between uselessly safe and dangerously autonomous

How Cowork differs from Claude Code: coding evals vs. knowledge-work evals, different system-prompt tradeoffs, longer planning horizons, and heavier use of planning and clarification tools

Why skills matter: simple markdown-based instructions as a lightweight abstraction layer for reusable workflows, personalized automation, and portable agent behavior

Skills vs. MCPs: why Felix is increasingly interested in file-based, text-native interfaces that tell the model what to do, rather than forcing everything through rigid tool schemas

The portability problem: why personal skills should move across agent products, and the unresolved tension between public reusable workflows and private user-specific context

Real use cases already happening today: uploading videos, organizing files, handling taxes, managing calendars, debugging internal crashes, analyzing finances, and automating repetitive browser workflows

Why AI products should work with your existing stack: Anthropic\u2019s bias toward integrating with Chrome, Office, and existing workflows inst