# Retrieval After RAG: Hybrid Search, Agents, and Database Design — Simon Hørup Eskildsen of Turbopuffer

**Source:** Latent Space  
**Date:** 2026-03-12  
**URL:** https://www.latent.space/p/turbopuffer  
**Tier:** 1  

---

Turbopuffer came out of a reading app.

In 2022, Simon was helping his friends at Readwise scale their infra for a highly requested feature: article recommendations and semantic search. Readwise was paying ~$5k/month for their relational database and vector search would cost ~$20k/month making the feature too expensive to ship. In 2023 after mulling over the problem from Readwise, Simon decided he wanted to “build a search engine” which became Turbopuffer.

Turbopuffer helping Readwise today - https://turbopuffer.com/customers/readwise

We discuss:
• Simon’s path: Denmark → Shopify infra for nearly a decade → “angel engineering” across startups like Readwise, Replicate, and Causal → turbopuffer almost accidentally becoming a company 
• The Readwise origin story: building an early recommendation engine right after the ChatGPT moment, seeing it work, then realizing it would cost ~$30k/month for a company spending ~$5k/month total on infra and getting obsessed with fixing that cost structure 
• Why turbopuffer is “a search engine for unstructured data”: Simon’s belief that models can learn to reason, but can’t compress the world’s knowledge into a few terabytes of weights, so they need to connect to systems that hold truth in full fidelity 
• The three ingredients for building a great database company: a new workload, a new storage architecture, and the ability to eventually support every query plan customers will want on their data 
• The architecture bet behind turbopuffer: going all in on object storage and NVMe, avoiding a traditional consensus layer, and building around the cloud primitives that only became possible in the last few years 

Simon Eskildsen@Sirupsen
our tiered storage engine keeps getting better, seamlessly letting you navigate cost/latency tradeoffs.

not benchmarks, but in production, on real workloads.

query once in a while? Object storage
query sometimes? NVMe
query a lot? NVMe/memory
turbopuffer @turbopufferproduction latency is all that matters, big drops over the past few weeks 📉

big things in the pipes to make turbopuffer even faster.

(p99 are cold queries completely from object storage)3:14 PM · Apr 19, 2024 · 8.26K Views3 Reposts · 43 Likes

• Why Simon hated operating Elasticsearch at Shopify: years of painful on-call experience shaped his obsession with simplicity, performance, and eliminating state spread across multiple systems 
• The Cursor story: launching turbopuffer as a scrappy side project, getting an email from Cursor the next day, flying out after a 4am call, and helping cut Cursor’s costs by 95% while fixing their per-user economics 

turbopuffer@turbopuffer
cursor wrote about how semantic search with turbopuffer improves their agent's accuracy
Cursor @cursor_aiSemantic search improves our agent's accuracy across all frontier models, especially in large codebases where grep alone falls short.

Learn more about our results and how we trained an embedding model for retrieving code.2:31 PM · Nov 6, 2025 · 26.7K Views2 Reposts · 148 Likes

• The Notion story: buying dark fiber, tuning TCP windows, and eating cross-cloud costs because Simon refused to compromise on architecture just to close a deal faster 

Akshay Kothari@akothari
It’d be unimaginable to build Notion AI without Turbopuffer. Excellent product, even better people.
Simon Eskildsen @SirupsenAn incredible year for turbopuffer is closing. We now manage trillions of vectors and tens of petabytes. We’ve puffed up revenue 10x and headcount 5x.

We’ve helped Anthropic, Cursor, Notion and others connect every petabyte to AI to ship the most ambitious version of their4:49 PM · Dec 18, 2025 · 11.2K Views3 Replies · 2 Reposts · 98 Likes

• Why AI changes the build-vs-buy equation: it’s less about whether a company can build search infra internally, and more about whether they have time especially if an external team can feel like an extension of their own 
• Why RAG isn’t dead: coding companies still rely heavily on search, and Simon sees hybrid retrieval semantic, text, regex, SQL-style patterns becoming more important, not less 
• How agentic workloads are changing search: the old pattern was one retrieval call up front; the new pattern is one agent firing many parallel queries at once, turning search into a highly concurrent tool call 
• Why turbopuffer is reducing query pricing: agentic systems are dramatically increasing query volume, and Simon expects retrieval infra to adapt to huge bursts of concurrent search rather than a small number of carefully chosen calls 
• The philosophy of “playing with open cards”: Simon’s habit of being radically honest with investors, including telling Lachy Groom he’d return the money if turbopuffer didn’t hit PMF by year-end 
• The “P99 engineer”: Simon’s framework for building a talent-dense company, rejecting by default unless someone on the team feels strongly enough to fight for the candidate 

Simon Eskildsen@Sirupsen
we are looking for a p99 engineer to work on infra/autoscaling/k8s tooling for the 10s of clusters (soon 100s) we run across all 3 clouds.

dm me3:38 PM · Jun 5, 2025 · 18.8K Views5 Replies · 17 Reposts · 134 Likes
—

Simon Hørup Eskildsen
• LinkedIn: https://www.linkedin.com/in/sirupsen
• X: https://x.com/Sirupsen
• https://sirupsen.com/about

turbopuffer
• https://turbopuffer.com/

## Full Video Pod

## Timestamps

00:00:00 The PMF promise to Lachy Groom
00:00:25 Intro and Simon's background
00:02:19 What turbopuffer actually is
00:06:26 Shopify, Elasticsearch, and the pain behind the company
00:10:07 The Readwise experiment that sparked turbopuffer
00:12:00 The insight Simon couldn’t stop thinking about
00:17:00 S3 consistency, NVMe, and the architecture bet
00:20:12 The Notion story: latency, dark fiber, and conviction
00:25:03 Build vs. buy in the age of AI
00:26:00 The Cursor story: early launch to breakout customer
00:29:00 Why code search still matters
00:32:00 Search in the age of agents
00:34:22 Pricing turbopuffer in the AI era
00:38:17 Why Simon chose Lachy Groom
00:41:28 Becoming a founder on purpose
00:44:00 The “P99 engineer” philosophy
00:49:30 Bending software to your will
00:51:13 The future of turbopuffer
00:57:05 Simon’s tea obsession
00:59:03 Tea kits, X Live, and P99 Live

## Transcript

Simon Hørup Eskildsen: I don’t think I’ve said this publicly before, but I just called Lockey and was like, local Lockie. Like if this doesn’t have PMF by the end of the year, like we’ll just like return all the money to you. But it’s just like, I don’t really, we, Justine and I don’t wanna work on this unless it’s really working.

So we want to give it the best shot this year and like we’re really gonna go for it. We’re gonna hire a bunch of people. We’re just gonna be honest with everyone. Like when I don’t know how to play a game, I just play with open cards. Lockey was the only person that didn’t, that didn’t freak out. He was like, I’ve never heard anyone say that before.

Alessio: Hey everyone, welcome to the Leading Space podcast. This is Celesio Pando, Colonel Laz, and I’m joined by Swix, editor of Leading Space.

swyx: Hello. Hello, uh, we’re still, uh, recording in the Ker studio for the first time. Very excited. And today we are joined by Simon Eski. Of Turbo Farer welcome.

Simon Hørup Eskildsen: Thank you so much for having me.

swyx: Turbo Farer has like really gone on a huge tear, and I, I do have to mention that like you’re one of, you’re not my newest member of the Danish AHU Mafia, where like there’s a lot of legendary programmers that have come out of it, like, uh, beyond Trotro, Rasmus, lado Berg and the V eight team and, and Google Maps team.

Uh, you’re mostly a Canadian now, but isn’t that interesting? There’s so many, so much like strong Danish presence.

Simon Hørup Eskildsen: Yeah, I was writing a post, um, not that long ago about sort of the influences. So I grew up in Denmark, right? I left, I left when, when I was 18 to go to Canada to, to work at Shopify. Um, and so I, like, I’ve, I would still say that I feel more Danish than, than Canadian.

This is also the weird accent. I can’t say th because it, this is like, I don’t, you know, my wife is also Canadian, um, and I think. I think like one of the things in, in Denmark is just like, there’s just such a ruthless pragmatism and there’s also a big focus on just aesthetics. Like, they’re like very, people really care about like where, what things look like.

Um, and like Canada has a lot of attributes, US has, has a lot of attributes, but I think there’s been lots of the great things to carry. I don’t know what’s in the water in Ahu though. Um, and I don’t know that I could be considered part of the Mafi mafia quite yet, uh, compared to the phenomenal individuals we just mentioned.

Barra OV is also, uh, Danish Canadian. Okay. Yeah. I don’t know where he lives now, but, and he’s the PHP.

swyx: Yeah. And obviously Toby German, but moved to Canada as well. Yes. Like this is like import that, uh, that, that is an interesting, um, talent move.

Alessio: I think. I would love to get from you. Definition of Turbo puffer, because I think you could be a Vector db, which is maybe a bad word now in some circles, you could be a search engine.

It’s like, let, let’s just start there and then we’ll maybe run through the history of how you got to this point.

Simon Hørup Eskildsen: For sure. Yeah. So Turbo Puffer is at this point in time, a search engine, right? We do full text search and we do vector search, and that’s really what we’re specialized in. If you’re trying to do much more than that, like then this might not be the right place yet, but Turbo Buffer is all about search.

The other way that I think about it is that we can take all of the world’s knowledge, all of the exabytes and exabytes of data that there is, and we can use those tokens to train a model, but we can’t compress all of that into a few terabytes of weights, right? Compress into a few terabytes of weights, how to reason with the world, how to make sense of the knowledge.

But we have to somehow connect it to something externally that actually holds that like in full fidelity and truth. Um, and that’s the thing that we intend to become. Right? That’s like a very holier than now kind of phrasing, right? But being the search engine for unstructured, unstructured data is the focus of turbo puffer at this point in time.

Alessio: And let’s break down. So people might say, well, didn’t Elasticsearch already do this? And then some other people might say, is this search on my data, is this like closer to rag than to like a xr, like a public search thing? Like how, how do you segment like the different types of search?

Simon Hørup Eskildsen: The way that I generally think about this is like, there’s a lot of database companies and I think if you wanna build a really big database company, sort of, you need a couple of ingredients to be in the air.

We don’t, which only happens roughly every 15 years. You need a new workload. You basically need the ambition that every single company on earth is gonna have data in your database. Multiple times you look at a company like Oracle, right? You will, like, I don’t think you can find a company on earth with a digital presence that it not, doesn’t somehow have some data in an Oracle database.

Right? And I think at this point, that’s also true for Snowflake and Databricks, right? 15 years later it’s, or even more than that, there’s not a company on earth that doesn’t, in. Or directly is consuming Snowflake or, or Databricks or any of the big analytics databases. Um, and I think we’re in that kind of moment now, right?

I don’t think you’re gonna find a company over the next few years that doesn’t directly or indirectly, um, have all their data available for, for search and connect it to ai. So you need that new workload, like you need something to be happening where there’s a new workload that causes that to happen, and that new workload is connecting very large amounts of data to ai.

The second thing you need. The second condition to build a big database company is that you need some new underlying change in the storage architecture that is not possible from the databases that have come before you. If you look at Snowflake and Databricks, right, commoditized, like massive fleet of HDDs, like that was not possible in it.

It just wasn’t in the air in the nineties, right? So you just didn’t, we just didn’t build these systems. S3 and and and so on was not around. And I think the architecture that is now possible that wasn’t possible 15 years ago is to go all in on NVME SSDs. It requires a particular type of architecture for the database that.

It’s difficult to retrofit onto the databases that are already there, including the ones you just mentioned. The second thing is to go all in on OIC storage, more so than we could have done 15 years ago. Like we don’t have a consensus layer, we don’t really have anything. In fact, you could turn off all the servers that Turbo Buffer has, and we would not lose any data because we have all completely all in on OIC storage.

And this means that our architecture is just so simple. So that’s the second condition, right? First being a new workload. That means that every company on earth, either indirectly or directly, is using your database. Second being, there’s some new storage architecture. That means that the, the companies that have come before you can do what you’re doing.

I think the third thing you need to do to build a big database company is that over time you have to implement more or less every Cory plan on the data. What that means is that you. You can’t just get stuck in, like, this is the one thing that a database does. It has to be ever evolving because when someone has data in the database, they over time expect to be able to ask it more or less every question.

So you have to do that to get the storage architecture to the limit of what, what it’s capable of. Those are the three conditions.

swyx: I just wanted to get a little bit of like the motivation, right? Like, so you left Shopify, you’re like principal, engineer, infra guy. Um, you also head of kernel labs, uh, inside of Shopify, right?

And then you consulted for read wise and that it kind of gave you that, that idea. I just wanted you to tell that story. Um, maybe I, you’ve told it before, but, uh, just introduce the, the. People to like the, the new workload, the sort of aha moment for turbo Puffer

Simon Hørup Eskildsen: For sure. So yeah, I spent almost a decade at Shopify.

I was on the infrastructure team, um, from the fairly, fairly early days around 2013. Um, at the time it felt like it was growing so quickly and everything, all the metrics were, you know, doubling year on year compared to the, what companies are contending with today. It’s very cute in growth. I feel like lot some companies are seeing that month over month.

Um, of course. Shopify compound has been compounding for a very long time now, but I spent a decade doing that and the majority of that was just make sure the site is up today and make sure it’s up a year from now. And a lot of that was really just the, um, you know, uh, the Kardashians would drive very, very large amounts of, of data to, to uh, to Shopify as they were rotating through all the merch and building out their businesses.

And we just needed to make sure we could handle that. Right. And sometimes these were events, a million requests per second. And so, you know, we, we had our own data centers back in the day and we were moving to the cloud and there was so much sharding work and all of that that we were doing. So I spent a decade just scaling databases ‘cause that’s fundamentally what’s the most difficult thing to scale about these sites.

The database that was the most difficult for me to scale during that time, and that was the most aggravating to be on call for, was elastic search. It was very, very difficult to deal with. And I saw a lot of projects that were just being held back in their ambition by using it.

swyx: And I mean, self-hosted.

Self-hosted. ‘cause

Simon Hørup Eskildsen: it’s, yeah, and it commercial, this is like 2015, right? So it’s like a very particular vintage. Right. It’s probably better at a lot of these things now. Um, it was difficult to contend with and I’m just like, I just think about it. It’s an inverted index. It should be good at these kinds of queries and do all of this.

And it was, we, we often couldn’t get it to do exactly what we needed to do or basically get lucine to do, like expose lucine raw to, to, to what we needed to do. Um, so that was like. Just something that we did on the side and just panic scaled when we needed to, but not a particular focus of mine. So I left, and when I left, I, um, wasn’t sure exactly what I wanted to do.

I mean, it spent like a decade inside of the same company. I’d like grown up there. I started working there when I was 18.

swyx: You only do Rails?

Simon Hørup Eskildsen: Yeah. I mean, yeah. Rails. And he’s a Rails guy. Uh, love Rails. So good. Um,

Alessio: we all wish we could still work in Rails.

swyx: I know know. I know, but some, I tried learning Ruby.

It’s just too much, like too many options to do the same thing. It’s, that’s my, I I know there’s a, there’s a way to do it.

Simon Hørup Eskildsen: I love it. I don’t know that I would use it now, like given cloud code and, and, and cursor and everything, but, um, um, but still it, like if I’m just sitting down and writing a teal code, that’s how I think.

But anyway, I left and I wasn’t, I talked to a couple companies and I was like, I don’t. I need to see a little bit more of the world here to know what I’m gonna like focus on next. Um, and so what I decided is like I was gonna, I called it like angel engineering, where I just hopped around in my friend’s companies in three months increments and just helped them out with something.

Right. And, and just vested a bit of equity and solved some interesting infrastructure problem. So I worked with a bunch of companies at the time, um, read Wise was one of them. Replicate was one of them. Um, causal, I dunno if you’ve tried this, it’s like a, it’s a spreadsheet engine Yeah. Where you can do distribution.

They sold recently. Yeah. Um, we’ve been, we used that in fp and a at, um, at Turbo Puffer. Um, so a bunch of companies like this and it was super fun. And so we’re the Chachi bt moment happened, I was with. With read Wise for a stint, we were preparing for the reader launch, right? Which is where you, you cue articles and read them later.

And I was just getting their Postgres up to snuff, like, which basically boils down to tuning, auto vacuum. So I was doing that and then this happened and we were like, oh, maybe we should build a little recommendation engine and some features to try to hook in the lms. They were not that good yet, but it was clear there was something there.

And so I built a small recommendation engine just, okay, let’s take the articles that you’ve recently read, right? Like embed all the articles and then do recommendations. It was good enough that when I ran it on one of the co-founders of Rey’s, like I found out that I got articles about, about having a child.

I’m like, oh my God, I didn’t, I, I didn’t know that, that they were having a child. I wasn’t sure what to do with that information, but the recommendation engine was good enough that it was suggesting articles, um, about that. And so there was, there was recommendations and uh, it actually worked really well.

But this was a company that was spending maybe five grand a month in total on all their infrastructure and. When I did the napkin math on running the embeddings of all the articles, putting them into a vector index, putting it in prod, it’s gonna be like 30 grand a month. That just wasn’t tenable. Right?

Like Read Wise is a proudly bootstrapped company and it’s paying 30 grand for infrastructure for one feature versus five. It just wasn’t tenable. So sort of in the bucket of this is useful, it’s pretty good, but let us, let’s return to it when the costs come down.

swyx: Did you say it grows by feature? So for five to 30 is by the number of, like, what’s the, what’s the Scaling factor scale?

It scales by the number of articles that you embed.

Simon Hørup Eskildsen: It does, but what I meant by that is like five grand for like all of the other, like the Heroku, dinos, Postgres, like all the other, and this then storage is 30. Yeah. And then like 30 grand for one feature. Right. Which is like, what other articles are related to this one.

Um, so it was just too much right to, to power everything. Their budget would’ve been maybe a few thousand dollars, which still would’ve been a lot. And so we put it in a bucket of, okay, we’re gonna do that later. We’ll wait, we will wait for the cost to come down. And that haunted me. I couldn’t stop thinking about it.

I was like, okay, there’s clearly some latent demand here. If the cost had been a 10th, we would’ve shipped it and. This was really the only data point that I had. Right. I didn’t, I, I didn’t, I didn’t go out and talk to anyone else. It was just so I started reading Right. I couldn’t, I couldn’t help myself.

Like I didn’t know what like a vector index is. I, I generally barely do about how to generate the vectors. There was a lot of hype about, this is a early 2023. There was a lot of hype about vector databases. There were raising a lot of money and it’s like, I really didn’t know anything about it. It’s like, you know, trying these little models, fine tuning them.

Like I was just trying to get sort of a lay of the land. So I just sat down. I have this. A GitHub repository called Napkin Math. And on napkin math, there’s just, um, rows of like, oh, this is how much bandwidth. Like this is how many, you know, you can do 25 gigabytes per second on average to dram. You can do, you know, five gigabytes per second of rights to an SSD, blah blah.

All of these numbers, right? And S3, how many you could do per, how much bandwidth can you drive per connection? I was just sitting down, I was like, why hasn’t anyone build a database where you just put everything on O storage and then you puff it into NVME when you use the data and you puff it into dram if you’re, if you’re querying it alive, it’s just like, this seems fairly obvious and you, the only real downside to that is that if you go all in on o storage, every right will take a couple hundred milliseconds of latency, but from there it’s really all upside, right?

You do the first go, it takes half a second. And it sort of occurred to me as like, well. The architecture is really good for that. It’s really good for AB storage, it’s really good for nvm ESSD. It’s, well, you just couldn’t have done that 10 years ago. Back to what we were talking about before. You really have to build a database where you have as few round trips as possible, right?

This is how CPUs work today. It’s how NVM E SSDs work. It’s how as, um, as three works that you want to have a very large amount of outstanding requests, right? Like basically go to S3, do like that thousand requests to ask for data in one round trip. Wait for that. Get that, like, make a new decision. Do it again, and try to do that maybe a maximum of three times.

But no databases were designed that way within NVME as is ds. You can drive like within, you know, within a very low multiple of DRAM bandwidth if you use it that way. And same with S3, right? You can fully max out the network card, which generally is not maxed out. You get very, like, very, very good bandwidth.

And, but no one had built a database like that. So I was like, okay, well can’t you just, you know, take all the vectors right? And plot them in the proverbial coordinate system. Get the clusters, put a file on S3 called clusters, do json, and then put another file for every cluster, you know, cluster one, do js O cluster two, do js ON you know that like it’s two round trips, right?

So you get the clusters, you find the closest clusters, and then you download the cluster files like the, the closest end. And you could do this in two round trips.

swyx: You were nearest neighbors locally.

Simon Hørup Eskildsen: Yes. Yes. And then, and you would build this, this file, right? It’s just like ultra simplistic, but it’s not a far shot from what the first version of Turbo Buffer was.

Why hasn’t anyone done that

Alessio: in that moment? From a workload perspective, you’re thinking this is gonna be like a read heavy thing because they’re doing recommend. Like is the fact that like writes are so expensive now? Oh, with ai you’re actually not writing that much.

Simon Hørup Eskildsen: At that point I hadn’t really thought too much about, well no actually it was always clear to me that there was gonna be a lot of rights because at Shopify, the search clusters were doing, you know, I don’t know, tens or hundreds of crew QPS, right?

‘cause you just have to have a human sit and type in. But we did, you know, I don’t know how many updates there were per second. I’m sure it was in the millions, right into the cluster. So I always knew there was like a 10 to 100 ratio on the read write. In the read wise use case. It’s, um, even, even in the read wise use case, there’d probably be a lot fewer reads than writes, right?

There’s just a lot of churn on the amount of stuff that was going through versus the amount of queries. Um, I wasn’t thinking too much about that. I was mostly just thinking about what’s the fundamentally cheapest way to build a database in the cloud today using the primitives that you have available.

And this is it, right? You just, now you have one machine and you know, let’s say you have a terabyte of data in S3, you paid the $200 a month for that, and then maybe five to 10% of that data and needs to be an NV ME SSDs and less than that in dram. Well. You’re paying very, very little to inflate the data.

swyx: By the way, when you say no one else has done that, uh, would you consider Neon, uh, to be on a similar path in terms of being sort of S3 first and, uh, separating the compute and storage?

Simon Hørup Eskildsen: Yeah, I think what I meant with that is, uh, just build a completely new database. I don’t know if we were the first, like it was very much, it was, I mean, I, I hadn’t, I just looked at the napkin math and was like, this seems really obvious.

So I’m sure like a hundred people came up with it at the same time. Like the light bulb and every invention ever. Right. It was just in the air. I think Neon Neon was, was first to it. And they’re trying, they’re retrofitted onto Postgres, right? And then they built this whole architecture where you have, you have it in memory and then you sort of.

You know, m map back to S3. And I think that was very novel at the time to do it for, for all LTP, but I hadn’t seen a database that was truly all in, right. Not retrofitting it. The database felt built purely for this no consensus layer. Even using compare and swap on optic storage to do consensus. I hadn’t seen anyone go that all in.

And I, I mean, there, there, I’m sure there was someone that did that before us. I don’t know. I was just looking at the napkin math

swyx: and, and when you say consensus layer, uh, are you strongly relying on S3 Strong consistency? You are. Okay.

So

Simon Hørup Eskildsen: that is your consensus layer. It, it is the consistency layer. And I think also, like, this is something that most people don’t realize, but S3 only became consistent in December of 2020.

swyx: I remember this coming out during COVID and like people were like, oh, like, it was like, uh, it was just like a free upgrade.

Simon Hørup Eskildsen: Yeah.

swyx: They were just, they just announced it. We saw consistency guys and like, okay, cool.

Simon Hørup Eskildsen: And I’m sure that they just, they probably had it in prod for a while and they’re just like, it’s done right.

And people were like, okay, cool. But. That’s a big moment, right? Like nv, ME SSDs, were also not in the cloud until around 2017, right? So you just sort of had like 2017 nv, ME SSDs, and people were like, okay, cool. There’s like one skew that does this, whatever, right? Takes a few years. And then the second thing is like S3 becomes consistent in 2020.

So now it means you don’t have to have this like big foundation DB or like zookeeper or whatever sitting there contending with the keys, which is how. You know, that’s what Snowflake and others have do so much

swyx: for gone

Simon Hørup Eskildsen: Exactly. Just gone. Right? And so just push to the, you know, whatever, how many hundreds of people they have working on S3 solved and then compare and swap was not in S3 at this point in time,

swyx: by the way.

Uh, I don’t know what that is, so maybe you wanna explain. Yes. Yeah.

Simon Hørup Eskildsen: Yes. So, um, what Compare and swap is, is basically, you can imagine that if you have a database, it might be really nice to have a file called metadata json. And metadata JSON could say things like, Hey, these keys are here and this file means that, and there’s lots of metadata that you have to operate in the database, right?

But that’s the simplest way to do it. So now you have might, you might have a lot of servers that wanna change the metadata. They might have written a file and want the metadata to contain that file. But you have a hundred nodes that are trying to contend with this metadata that JSON well, what compare and Swap allows you to do is basically just you download the file, you make the modifications, and then you write it only if it hasn’t changed.

While you did the modification and if not you retry. Right? Should just have this retry loops. Now you can imagine if you have a hundred nodes doing that, it’s gonna be really slow, but it will converge over time. That primitive was not available in S3. It wasn’t available in S3 until late 2024, but it was available in GCP.

The real story of this is certainly not that I sat down and like bake brained it. I was like, okay, we’re gonna start on GCS S3 is gonna get it later. Like it was really not that we started, we got really lucky, like we started on GCP and we started on GCP because tur um, Shopify ran on GCP. And so that was the platform I was most available with.

Right. Um, and I knew the Canadian team there ‘cause I’d worked with them at Shopify and so it was natural for us to start there. And so when we started building the database, we’re like, oh yeah, we have to build a, we really thought we had to build a consensus layer, like have a zookeeper or something to do this.

But then we discovered the compare and swap. It’s like, oh, we can kick the can. Like we’ll just do metadata r json and just, it’s fine. It’s probably fine. Um, and we just kept kicking the can until we had very, very strong conviction in the idea. Um, and then we kind of just hinged the company on the fact that S3 probably was gonna get this, it started getting really painful in like mid 2024.

‘cause we were closing deals with, um, um, notion actually that was running in AWS and we’re like, trust us. You, you really want us to run this in GCP? And they’re like, no, I don’t know about that. Like, we’re running everything in AWS and the latency across the cloud were so big and we had so much conviction that we bought like, you know, dark fiber between the AWS regions in, in Oregon, like in the InterExchange and GCP is like, we’ve never seen a startup like do like, what’s going on here?

And we’re just like, no, we don’t wanna do this. We were tuning like TCP windows, like everything to get the latency down ‘cause we had so high conviction in not doing like a, a metadata layer on S3. So those were the three conditions, right? Compare and swap. To do metadata, which wasn’t in S3 until late 2024 S3 being consistent, which didn’t happen until December, 2020.

Uh, 2020. And then NVMe ssd, which didn’t end in the cloud until 2017.

swyx: I mean, in some ways, like a very big like cloud success story that like you were able to like, uh, put this all together, but also doing things like doing, uh, bind our favor. That that actually is something I’ve never heard.

Simon Hørup Eskildsen: I mean, it’s very common when you’re a big company, right?

You’re like connecting your own like data center or whatever. But it’s like, it was uniquely just a pain with notion because the, um, the org, like most of the, like if you’re buying in Ashburn, Virginia, right? Like US East, the Google, like the GCP and, and AWS data centers are like within a millisecond on, on each other, on the public exchanges.

But in Oregon uniquely, the GCP data center sits like a couple hundred kilometers, like east of Portland and the AWS region sits in Portland, but the network exchange they go through is through Seattle. So it’s like a full, like 14 milliseconds or something like that. And so anyway, yeah. It’s, it’s, so we were like, okay, we can’t, we have to go through an exchange in Portland.

Yeah. And

swyx: you’d rather do this than like run your zookeeper and like

Simon Hørup Eskildsen: Yes. Way rather. It doesn’t have state, I don’t want state and two systems. Um, and I think all that is just informed by Justine, my co-founder and I had just been on call for so long. And the worst outages are the ones where you have state in multiple places that’s not syncing up.

So it really came from, from a a, like just a, a very pure source of pain, of just imagining what we would be Okay. Being woken up at 3:00 AM about and having something in zookeeper was not one of them.

swyx: You, you’re talking to like a notion or something. Do they care or do they just, they

Simon Hørup Eskildsen: just, they care about latency.

swyx: They latency cost. That’s it.

Simon Hørup Eskildsen: They just cared about latency. Right. And we just absorbed the cost. We’re just like, we have high conviction in this. At some point we can move them to AWS. Right. And so we just, we, we’ll buy the fiber, it doesn’t matter. Right. Um, and it’s like $5,000. Usually when you buy fiber, you buy like multiple lines.

And we’re like, we can only afford one, but we will just test it that when it goes over the public internet, it’s like super smooth. And so we did a lot of, anyway, it’s, yeah, it was, that’s cool.

Alessio: You can imagine talking to the GCP rep and it’s like, no, we’re gonna buy, because we know we’re gonna turn, we’re gonna turn from you guys and go to AWS in like six months.

But in the meantime we’ll do this. It’s

Simon Hørup Eskildsen: a, I mean, like they, you know, this workload still runs on GCP for what it’s worth. Right? ‘cause it’s so, it was just, it was so reliable. So it was never about moving off GCP, it was just about honesty. It was just about giving notion the latency that they deserved.

Right. Um, and we didn’t want ‘em to have to care about any of this. We also, they were like, oh, egress is gonna be bad. It was like, okay, screw it. Like we’re just gonna like vvc, VPC peer with you and AWS we’ll eat the cost. Yeah. Whatever needs to be done.

Alessio: And what were the actual workloads? Because I think when you think about ai, it’s like 14 milliseconds.

It’s like really doesn’t really matter in the scheme of like a model generation.

Simon Hørup Eskildsen: Yeah. We were told the latency, right. That we had to beat. Oh, right. So, so we’re just looking at the traces. Right. And then sort of like hand draw, like, you know, kind of like looking at the trace and then thinking what are the other extensions of the trace?

Right. And there’s a lot more to it because it’s also when you have, if you have 14 versus seven milliseconds, right. You can fit in another round trip. So we had to tune TCP to try to send as much data in every round trip, prewarm all the connections. And there was, there’s a lot of things that compound from having these kinds of round trips, but in the grand scheme it was just like, well, we have to beat the latency of whatever we’re up against.

swyx: Which is like they, I mean, notion is a database company. They could have done this themselves. They, they do lots of database engineering themselves. How do you even get in the door? Like Yeah, just like talk through that kind of.

Simon Hørup Eskildsen: Last time I was in San Francisco, I was talking to one of the engineers actually, who, who was one of our champions, um, at, AT Notion.

And they were, they were just trying to make sure that the, you know, per user cost matched the economics that they needed. You know, Uhhuh like, it’s like the way I think about, it’s like I have to earn a return on whatever the clouds charge me and then my customers have to earn a return on that. And it’s like very simple, right?

And so there has to be gross margin all the way up and that’s how you build the product. And so then our customers have to make the right set of trade off the turbo Puffer makes, and if they’re happy with that, that’s great.

swyx: Do you feel like you’re competing with build internally versus buy or buy versus buy?

Simon Hørup Eskildsen: Yeah, so, sorry, this was all to build up to your question. So one of the notion engineers told me that they’d sat and probably on a napkin, like drawn out like, why hasn’t anyone built this? And then they saw terrible. It was like, well, it literally that. So, and I think AI has also changed the buy versus build equation in terms of, it’s not really about can we build it, it’s about do we have time to build it?

I think they like, I think they felt like, okay, if this is a team that can do that and they, they feel enough like an extension of our team, well then we can go a lot faster, which would be very, very good for them. And I mean, they put us through the, through the test, right? Like we had some very, very long nights to to, to do that POC.

And they were really our biggest, our second big customer off the cursor, which also was a lot of late nights. Right.

swyx: Yeah. That, I mean, should we go into that story? The, the, the sort of Chris’s story, like a lot, um, they credit you a lot for. Working very closely with them. So I just wanna hear, I’ve heard this, uh, story from Sole’s point of view, but like, I’m curious what, what it looks like from your side.

Simon Hørup Eskildsen: I actually haven’t heard it from Sole’s point of view, so maybe you can now cross reference it. The way that I remember it was that, um, the day after we launched, which was just, you know, I’d worked the whole summer on, on the first version. Justine wasn’t part of it yet. ‘cause I just, I didn’t tell anyone that summer that I was working on this.

I was just locked in on building it because it’s very easy otherwise to confuse talking about something to actually doing it. And so I was just like, I’m not gonna do that. I’m just gonna do the thing. I launched it and at this point turbo puffer is like a rust binary running on a single eight core machine in a T Marks instance.

And me deploying it was like looking at the request log and then like command seeing it or like control seeing it to just like, okay, there’s no request. Let’s upgrade the binary. Like it was like literally the, the, the, the scrappiest thing. You could imagine it was on purpose because just like at Shopify, we did that all the time.

Like, we like move, like we ran things in tux all the time to begin with. Before something had like, at least the inkling of PMF, it was like, okay, is anyone gonna hear about this? Um, and one of the cursor co-founders Arvid reached out and he just, you know, the, the cursor team are like all I-O-I-I-M-O like, um, contenders, right?

So they just speak in bullet points and, and facts. It was like this amazing email exchange just of, this is how many QPS we have, this is what we’re paying, this is where we’re going, blah, blah, blah. And so we’re just conversing in bullet points. And I tried to get a call with them a few times, but they were, so, they were like really writing the PMF bowl here, just like late 2023.

And one time Swally emails me at like five. What was it like 4:00 AM Pacific time saying like, Hey, are you open for a call now? And I’m on the East coast and I, it was like 7:00 AM I was like, yeah, great, sure, whatever. Um, and we just started talking and something. Then I didn’t know anything about sales.

It was something that just comp compelled me. I have to go see this team. Like, there’s something here. So I, I went to San Francisco and I went to their office and the way that I remember it is that Postgres was down when I showed up at the office. Did SW tell you this? No. Okay. So Postgres was down and so it’s like they were distracting with that.

And I was trying my best to see if I could, if I could help in any way. Like I knew a little bit about databases back to tuning, auto vacuum. It was like, I think you have to tune out a vacuum. Um, and so we, we talked about that and then, um, that evening just talked about like what would it look like, what would it look like to work with us?

And I just said. Look like we’re all in, like we will just do what we’ll do whatever, whatever you tell us, right? They migrated everything over the next like week or two, and we reduced their cost by 95%, which I think like kind of fixed their per user economics. Um, and it solved a lot of other things. And we were just, Justine, this is also when I asked Justine to come on as my co-founder, she was the best engineer, um, that I ever worked with at Shopify.

She lived two blocks away and we were just, okay, we’re just gonna get this done. Um, and we did, and so we helped them migrate and we just worked like hell over the next like month or two to make sure that we were never an issue. And that was, that was the cursor story. Yeah.

swyx: And, and is code a different workload than normal text?

I, I don’t know. Is is it just text? Is it the same thing?

Simon Hørup Eskildsen: Yeah, so cursor’s workload is basically, they, um, they will embed the entire code base, right? So they, they will like chunk it up in whatever they would, they do. They have their own embedding model, um, which they’ve been public about. Um, and they find that on, on, on their evals.

It. There’s one of their evals where it’s like a 25% improvement on a very particular workload. They have a bunch of blog posts about it. Um, I think it works best on larger code basis, but they’ve trained their own embedding model to do this. Um, and so you’ll see it if you use the cursor agent, it will do searches.

And they’ve also been public around, um, how they’ve, I think they post trained their model to be very good at semantic search as well. Um, and that’s, that’s how they use it. And so it’s very good at, like, can you find me on the code that’s similar to this, or code that does this? And just in, in this queries, they also use GR to supplement it.

swyx: Yeah.

Simon Hørup Eskildsen: Um, of course

swyx: it’s been a big topic of discussion like, is rag dead because gr you know,

Simon Hørup Eskildsen: and I mean like, I just, we, we see lots of demand from the coding company to ethics

swyx: search in every part. Yes.

Simon Hørup Eskildsen: Uh, we, we, we see demand. And so, I mean, I’m. I like case studies. I don’t like, like just doing like thought pieces on this is where it’s going.

And like trying to be all macroeconomic about ai, that’s has turned out to be a giant waste of time because no one can really predict any of this. So I just collect case studies and I mean, cursor has done a great job talking about what they’re doing and I hope some of the other coding labs that use Turbo Puffer will do the same.

Um, but it does seem to make a difference for particular queries. Um, I mean we can also do text, we can also do RegX, but I should also say that cursors like security posture into Tur Puffer is exceptional, right? They have their own embedding model, which makes it very difficult to reverse engineer. They obfuscate the file paths.

They like you. It’s very difficult to learn anything about a code base by looking at it. And the other thing they do too is that for their customers, they encrypt it with their encryption keys in turbo puffer’s bucket. Um, so it’s, it’s, it’s really, really well designed.

swyx: And so this is like extra stuff they did to work with you because you are not part of Cursor.

Exactly like, and this is just best practice when working in any database, not just you guys. Okay. Yeah, that makes sense. Yeah. I think for me, like the, the, the learning is kind of like you, like all workloads are hybrid. Like, you know, uh, like you, you want the semantic, you want the text, you want the RegX, you want sql.

I dunno. Um, but like, it’s silly to like be all in on like one particularly query pattern.

Simon Hørup Eskildsen: I think, like I really like the way that, um, um, that swally at cursor talks about it, which is, um, I’m gonna butcher it here. Um, and you know, I’m a, I’m a database scalability person. I’m not a, I, I dunno anything about training models other than, um, what the internet tells me and what.

The way he describes is that this is just like cash compute, right? It’s like you have a point in time where you’re looking at some particular context and focused on some chunk and you say, this is the layer of the neural net at this point in time. That seems fundamentally really useful to do cash compute like that.

And, um, how the value of that will change over time. I’m, I’m not sure, but there seems to be a lot of value in that.

Alessio: Maybe talk a bit about the evolution of the workload, because even like search, like maybe two years ago it was like one search at the start of like an LLM query to build the context. Now you have a gentech search, however you wanna call it, where like the model is both writing and changing the code and it’s searching it again later.

Yeah. What are maybe some of the new types of workloads or like changes you’ve had to make to your architecture for it?

Simon Hørup Eskildsen: I think you’re right. When I think of rag, I think of, Hey, there’s an 8,000 token, uh, context window and you better make it count. Um, and search was a way to do that now. Everything is moving towards the, just let the agent do its thing.

Right? And so back to the thing before, right? The LLM is very good at reasoning with the data, and so we’re just the tool call, right? And that’s increasingly what we see our customers doing. Um, what we’re seeing more demand from, from our customers now is to do a lot of concurrency, right? Like Notion does a ridiculous amount of queries in every round trip just because they can’t.

And I’m also now, when I use the cursor agent, I also see them doing more concurrency than I’ve ever seen before. So a bit similar to how we designed a database to drive as much concurrency in every round trip as possible. That’s also what the agents are doing. So that’s new. It means just an enormous amount of queries all at once to the dataset while it’s warm in as few turns as possible.

swyx: Can I clarify one thing on that?

Simon Hørup Eskildsen: Yes.

swyx: Is it, are they batching multiple users or one user is driving multiple,

Simon Hørup Eskildsen: one user driving multiple, one agent driving.

swyx: It’s parallel searching a bunch of things.

Simon Hørup Eskildsen: Exactly.

swyx: Yeah. Yeah, exactly. So yeah, the clinician also did, did this for the fast context thing, like eight parallel at once.

Simon Hørup Eskildsen: Yes.

swyx: And, and like an interesting problem is, well, how do you make sure you have enough diversity so you’re not making the the same request eight times?

Simon Hørup Eskildsen: And I think like that’s probably also where the hybrid comes in, where. That’s another way to diversify. It’s a completely different way to, to do the search.

That’s a big change, right? So before it was really just like one call and then, you know, the LLM took however many seconds to return, but now we just see an enormous amount of queries. So the, um, we just see more queries. So we’ve like tried to reduce query, we’ve reduced query pricing. Um, this is probably the first time actually I’m saying that, but the query pricing is being reduced, like five x.

Um, and we’ll probably try to reduce it even more to accommodate some of these workloads of just doing very large amounts of queries. Um, that’s one thing that’s changed. I think the right, the right ratio is still very high, right? Like there’s still a, an enormous amount of rights per read, but we’re starting probably to see that change if people really lean into this pattern.

Alessio: Can we talk a little bit about the pricing? I’m curious, uh, because traditionally a database would charge on storage, but now you have the token generation that is so expensive, where like the actual. Value of like a good search query is like much higher because they’re like saving inference time down the line.

How do you structure that as like, what are people receptive to on the other side too?

Simon Hørup Eskildsen: Yeah. I, the, the turbo puffer pricing in the beginning was just very simple. The pricing on these on for search engines before Turbo Puffer was very server full, right? It was like, here’s the vm, here’s the per hour cost, right?

Great. And I just sat down with like a piece of paper and said like, if Turbo Puffer was like really good, this is probably what it would cost with a little bit of margin. And that was the first pricing of Turbo Puffer. And I just like sat down and I was like, okay, like this is like probably the storage amp, but whenever on a piece of paper I, it was vibe pricing.

It was very vibe price, and I got it wrong. Oh. Um, well I didn’t get it wrong, but like Turbo Puffer wasn’t at the first principle pricing, right? So when Cursor came on Turbo Puffer, it was like. Like, I didn’t know any VCs. I didn’t know, like I was just like, I don’t know, I didn’t know anything about raising money or anything like that.

I just saw that my GCP bill was, was high, was a lot higher than the cursor bill. So Justine and I was just like, well, we have to optimize it. Um, and I mean, to the chagrin now of, of it, of, of the VCs, it now means that we’re profitable because we’ve had so much pricing pressure in the beginning. Because it was running on my credit card and Justine and I had spent like, like tens of thousands of dollars on like compute bills and like spinning off the company and like very like, like bad Canadian lawyers and like things like to like get all of this done because we just like, we didn’t know.

Right. If you’re like steeped in San Francisco, you’re just like, you just know. Okay. Like you go out, raise a pre-seed round. I, I never heard a word pre-seed at this point in time.

swyx: When you had Cursor, you had Notion you, you had no funding.

Simon Hørup Eskildsen: Um, with Cursor we had no funding. Yeah. Um, by the time we had Notion Locke was, Locke was here.

Yeah. So it was really just, we vibe priced it 100% from first Principles, but it wasn’t, it, it was not performing at first principles, so we just did everything we could to optimize it in the beginning for that, so that at least we could have like a 5% margin or something. So I wasn’t freaking out because Cursor’s bill was also going like this as they were growing.

And so my liability and my credit limit was like actively like calling my bank. It was like, I need a bigger credit. Like it was, yeah. Anyway, that was the beginning. Yeah. But the pricing was, yeah, like storage rights and query. Right. And the, the pricing we have today is basically just that pricing with duct tape and spit to try to approach like, you know, like a, as a margin on the physical underlying hardware.

And we’re doing this year, you’re gonna see more and more pricing changes from us. Yeah.

swyx: And like is how much does stuff like VVC peering matter because you’re working in AWS land where egress is charged and all that, you know.

Simon Hørup Eskildsen: We probably don’t like, we have like an enterprise plan that just has like a base fee because we haven’t had time to figure out SKU pricing for all of this.

Um, but I mean, yeah, you can run turbo puffer either in SaaS, right? That’s what Cursor does. You can run it in a single tenant cluster. So it’s just you. That’s what Notion does. And then you can run it in, in, in BYOC where everything is inside the customer’s VPC, that’s what an for example, philanthropic does.

swyx: What I’m hearing is that this is probably the best CRO job for somebody who can come in and,

Simon Hørup Eskildsen: I mean,

swyx: help you with this.

Simon Hørup Eskildsen: Um, like Turbo Puffer hired, like, I don’t know what, what number this was, but we had a full-time CFO as like the 12th hire or something at Turbo Puffer, um, I think I hear are a lot of comp.

I don’t know how they do it. Like they have a hundred employees and not a CFO. It’s like having a CFO is like a running

swyx: business man. Like, you know,

Simon Hørup Eskildsen: it’s so good. Yeah, like money Mike, like he just, you know, just handles the money and a lot of the business stuff and so he came in and just hopped with a lot of the operational side of the business.

So like C-O-O-C-F-O, like somewhere in between.

swyx: Just as quick mention of Lucky, just ‘cause I’m curious, I’ve met Lock and like, he’s obviously a very good investor and now on physical intelligence, um, I call it generalist super angel, right? He invests in everything. Um, and I always wonder like, you know, is there something appealing about focusing on developer tooling, focusing on databases, going like, I’ve invested for 10 years in databases versus being like a lock where he can maybe like connect you to all the customers that you need.

Simon Hørup Eskildsen: This is an excellent question. No, no one’s asked me this. Um, why lockey? Because. There was a couple of people that we were talking to at the time and when we were raising, we were almost a little, we were like a bit distressed because one of our, one of our peers had just launched something that was very similar to Turbo Puffer.

And someone just gave me the advice at the time of just choose the person where you just feel like you can just pick up the phone and not prepare anything. And just be completely honest, and I don’t think I’ve said this publicly before, but I just called Lockey and was like local Lockie. Like if this doesn’t have PMF by the end of the year, like we’ll just like return all the money to you.

But it’s just like, I don’t really, we, Justine and I don’t wanna work on this unless it’s really working. So we want to give it the best shot this year and like we’re really gonna go for it. We’re gonna hire a bunch of people and we’re just gonna be honest with everyone. Like when I don’t know how to play a game, I just play with open cards and.

Lockey was the only person that didn’t, that didn’t freak out. He was like, I’ve never heard anyone say that before. As I said, I didn’t even know what a seed or pre-seed round was like before, probably even at this time. So I was just like very honest with him. And I asked him like, Lockie, have you ever have, have you ever invested in database company?

He was just like, no. And at the time I was like, am I dumb? Like, but I think there was something that just like really drew me to Lockie. He is so authentic, so honest, like, and there was something just like, I just felt like I could just play like, just say everything openly. And that was, that was, I think that that was like a perfect match at the time, and, and, and honestly still is.

He was just like, okay, that’s great. This is like the most honest, ridiculous thing I’ve ever heard anyone say to me. But like that, like that, why

swyx: is this ridiculous? Say competitor launch, this may not work out. It was

Simon Hørup Eskildsen: more just like. If this doesn’t work out, I’m gonna close up shop by the end of the mo the year, right?

Like it was, I don’t know, maybe it’s common. I, I don’t know. He told me it was uncommon. I don’t know. Um, that’s why we chose him and he’d been phenomenal. The other people were talking at the, at the time were database experts. Like they, you know, knew a lot about databases and Locke didn’t, this turned out to be a phenomenal asset.

Right. I like Justine and I know a lot about databases. The people that we hire know a lot about databases. What we needed was just someone who didn’t know a lot about databases, didn’t pretend to know a lot about databases, and just wanted to help us with candidates and customers. And he did. Yeah. And I have a list, right, of the investors that I have a relationship with, and Lockey has just performed excellent in the number of sub bullets of what we can attribute back to him.

Just absolutely incredible. And when people talk about like no ego and just the best thing for the founder, I like, I don’t think that anyone, like even my lawyer is like, yeah, Lockey is like the most friendly person you will find.

swyx: Okay. This is my most glow recommendation I’ve ever heard.

Alessio: He deserves it.

He’s very special.

swyx: Yeah. Yeah. Yeah. Okay. Amazing.

Alessio: Since you mentioned candidates, maybe we can talk about team building, you know, like, especially in sf, it feels like it’s just easier to start a company than to join a company. Uh, I’m curious your experience, especially not being n SF full-time and doing something that is maybe, you know, a very low level of detail and technical detail.

Simon Hørup Eskildsen: Yeah. So joining versus starting, I never thought that I would be a founder. I would start with it, like Turbo Puffer started as a blog post, and then it became a project and then sort of almost accidentally became a company. And now it feels like it’s, it’s like becoming a bigger company. That was never the intention.

The intentions were very pure. It’s just like, why hasn’t anyone done this? And it’s like, I wanna be the, like, I wanna be the first person to do it. I think some founders have this, like, I could never work for anyone else. I, I really don’t feel that way. Like, it’s just like, I wanna see this happen. And I wanna see it happen with some people that I really enjoy working with and I wanna have fun doing it and this, this, this has all felt very natural on that, on that sense.

So it was never a like join versus versus versus found. It was just dis found me at the right moment.

Alessio: Well I think there’s an argument for, you should have joined Cursor, right? So I’m curious like how you evaluate it. Okay, I should actually go raise money and make this a company versus like, this is like a company that is like growing like crazy.

It’s like an interesting technical problem. I should just build it within Cursor and then they don’t have to encrypt all this stuff. They don’t have to obfuscate things. Like was that on your mind at all or

Simon Hørup Eskildsen: before taking the, the small check from Lockie, I did have like a hard like look at myself in the mirror of like, okay, do I really want to do this?

And because if I take the money, I really have to do it right. And so the way I almost think about it’s like you kind of need to ha like you kind of need to be like fucked up enough to want to go all the way. And that was the conversation where I was like, okay, this is gonna be part of my life’s journey to build this company and do it in the best way that I possibly can’t.

Because if I ask people to join me, ask people to get on the cap table, then I have an ultimate responsibility to give it everything. And I don’t, I think some people, it doesn’t occur to me that everyone takes it that seriously. And maybe I take it too seriously, I don’t know. But that was like a very intentional moment.

And so then it was very clear like, okay, I’m gonna do this and I’m gonna give it everything.

Alessio: A lot of people don’t take it this seriously. But,

swyx: uh, let’s talk about, you have this concept of the P 99 engineer. Uh, people are 10 x saying, everyone’s saying, you know, uh, maybe engineers are out of a job. I don’t know.

But you definitely see a P 99 engineer, and I just want you to talk about it.

Simon Hørup Eskildsen: Yeah, so the P 99 engineer was just a term that we started using internally to talk about candidates and talk about how we wanted to build the company. And you know, like everyone else is, like we want a talent dense company.

And I think that’s almost become trite at this point. What I credit the cursor founders a lot with is that they just arrived there from first principles of like, we just need a talent dense, um, talent dense team. And I think I’ve seen some teams that weren’t talent dense and like seemed a counterfactual run, which if you’ve run in been in a large company, you will just see that like it’s just logically will happen at a large company.

Um, and so that was super important to me and Justine and it’s very difficult to maintain. And so we just needed, we needed wording for it. And so I have a document called Traits of the P 99 Engineer, and it’s a bullet point list. And I look at that list after every single interview that I do, and in every single recap that we do and every recap we end with.

End with, um, some version of I’m gonna reject this candidate completely regardless of what the discourse was, because I wanna see people fight for this person because the default should not be, we’re gonna hire this person. The default should be, we’re definitely not hiring this person. And you know, if everyone was like, ah, maybe throw a punch, then this is not the right.

swyx: Do, do you operate, like if there’s one cha there must have at least one champion who’s like, yes, I will put my career on, on, on the line for this. You know,

Simon Hørup Eskildsen: I think career on the line,

swyx: maybe a chair, but

Simon Hørup Eskildsen: yeah. You know, like, um, I would say so someone needs to like, have both fists up and be like, I’d fight.

Right? Yeah. Yeah. And if one person said, then, okay, let’s do it. Right?

swyx: Yeah.

Simon Hørup Eskildsen: Um. It doesn’t have to be absolutely everyone. Right? And like the interviews are always the sign that you’re checking for different attributes. And if someone is like knocking it outta the park in every single attribute, that’s, that’s fairly rare.

Um, but that’s really important. And so the traits of the P 99 engineer, there’s lots of them. There’s also the traits of the p like triple nine engineer and the quadruple nine engineer. This is like, it’s a long list.

swyx: Okay.

Simon Hørup Eskildsen: Um, I’ll give you some samples, right. Of what we, what we look for. I think that the P 99 engineer has some history of having bent, like their trajectory or something to their will.

Right? Some moment where it was just, they just, you know, made the computer do what it needed to do. There’s something like that, and it will, it will occur to have them at some point in their career. And, uh. Hopefully multiple times. Right.

swyx: Gimme an example of one of your engineers that like,

Simon Hørup Eskildsen: I’ll give an eng.

Uh, so we, we, we launched this thing called A and NV three. Um, we could, we’re also, we’re working on V four and V five right now, but a and NV three can search a hundred billion vectors with a P 50 of around 40 milliseconds and a p 99 of 200 milliseconds. Um, maybe other people have done this, I’m sure Google and others have done this, but, uh, we haven’t seen anyone, um, at least not in like a public consumable SaaS that can do this.

And that was an engineer, the chief architect of Turbo Puffer, Nathan, um, who more or less just bent this, the software was not capable of this and he just made it capable for a very particular workload in like a, you know, six to eight week period with the help of a lot of the team. Right. It’s been, been, there’s numerous of examples of that, like at, at turbo puff, but that’s like really bending the software and X 86 to your will.

It was incredible to watch. Um. You wanna see some moments like that?

swyx: Isn’t that triple nine?

Simon Hørup Eskildsen: Um, I think Nathan, what’s called

Alessio: group nine, that was only nine. I feel like this is too high for

Simon Hørup Eskildsen: Nathan. Nathan is, uh, Nathan is like, yeah, there’s a lot of nines. Okay. After that p So I think that’s one trait. I think another trait is that, uh, the P 99 spends a lot of time looking at maps.

Generally it’s their preferred ux. They just love looking at maps. You ever seen someone who just like, sits on their phone and just like, scrolls around on a map? Or did you not look at maps A lot? You guys don’t look at

swyx: maps? I guess I’m not feeling there. I don’t know, but

Simon Hørup Eskildsen: you just dis What about trains?

Do you like trains?

swyx: Uh, I mean they, not enough. Okay. This is just like weapon nice. Autism is what I call it. Like, like,

Simon Hørup Eskildsen: um, I love looking at maps, like, it’s like my preferred UX and just like I, you know, I like

swyx: lots

Alessio: of, of like random places, so

swyx: like,

you

swyx: know.

Alessio: Yes. Okay. There you go. So instead of like random places, like how do you explore the maps?

Simon Hørup Eskildsen: No, it’s, it’s just a joke.

swyx: It’s autism laugh. It’s like you are just obsessed by something and you like studying a thing.

Simon Hørup Eskildsen: The origin of this was that at some point I read an interview with some IOI gold medalist

swyx: Uhhuh,

Simon Hørup Eskildsen: and it’s like, what do you do in your spare time? I was just like, I like looking at maps.

I was like, I feel so seen. Like, I just like love, like swirling out. I was like, oh, Canada is so big. Where’s Baffin Island? I don’t know. I love it. Yeah. Um, anyway, so the traits of P 99, P 99 is obsessive, right? Like, there’s just like, you’ll, you’ll find traits of that we do an interview at, at, at, at turbo puffer or like multiple interviews that just try to screen for some of these things.

Um, so. There’s lots of others, but these are the kinds of traits that we look for.

swyx: I’ll tell you, uh, some people listen for like some of my dere stuff. Uh, I do think about derel as maps. Um, you draw a map for people, uh, maps show you the, uh, what is commonly agreed to be the geographical features of what a boundary is.

And it shows also shows you what is not doing. And I, I think a lot of like developer tools, companies try to tell you they can do everything, but like, let’s, let’s be real. Like you, your, your three landmarks are here, everyone comes here, then here, then here, and you draw a map and, and then you draw a journey through the map.

And like that. To me, that’s what developer relations looks like. So I do think about things that way.

Simon Hørup Eskildsen: I think the P 99 thinks in offs, right? The P 99 is very clear about, you know, hey, turbo puffer, you can’t run a high transaction workload on turbo puffer, right? It’s like the right latency is a hundred milliseconds.

That’s a clear trade off. I think the P 99 is very good at articulating the trade offs in every decision. Um. Which is exactly what the map is in your case, right?

swyx: Uh, yeah, yeah. My, my, my world. My world.

Alessio: How, how do you reconcile some of these things when you’re saying you bend the will the computer versus like the tradeoffs?

You know, I think sometimes it’s like, well, these are the tradeoffs, but the three nines, it’s like, actually it’s not a real trade off because we can make something that nobody has ever made before and actually make it work.

Simon Hørup Eskildsen: The way I think about the bending trajectory to your will is, um, if you sit down and do the napkin math, right, where you’re just like, okay, like if I have a hundred machines, they have this many terabytes of disc, they have this bandwidth, whatever, right?

And you sit down and you just do the like high school napkin math on this is how many qps we should be able to drive to it. Similar to how I did the vibe pricing, right? If you can sit down and do that, and then you observe the real system and you see, oh, we’re off by like 10 x bendings trajectory to your will is like just making the software get closer and closer to that first principle line.

The P 99 might even be able to cross the line Right. By finding even more optimizations than, than, than from first principle. So bending the software to your rail is about that, right? Like a hundred millisecond P 99 to um, to S3. I mean now you’re talking like someone really high agency that like goes to Seattle finds CS three team and it’s like, how are we gonna make this 10?

You know, like it’s that, that’s not quite what we talk about. Right. But yeah.

swyx: What’s the future? Turbo Puffer.

Simon Hørup Eskildsen: Turbo Puffer started out act one of Turbo Puffer was vector search. That was all we did to begin with Act two of Turbo Puffer is. Is and was full text Search Turbo Puffer today has a fairly start of the state-of-the-art full text search engine.

Um, we beat Lucine on some queries, in particular very long queries that we’ve optimized for because those are the text search queries we see today. They’re generated by LLMs or augmented by LLMs. Um, and we see them on Webscale datasets, right? Like someone searching for a very long texturing on all of Common Crawl.

We beat Lucine on some of those benchmarks and we expect to continue to beat Lucine on more and more queries. Um, that’s the performance and scale. Turbo Puffer does phenomenally now at full text search performance at scale. What we work on now is more and more features for full tech search. People expect a lot of features with full tech search.

And full tech search is still very valuable, right? If you go in and you press Command K and you search for si. Embedding based search might be like, oh, this is something agreeable. ‘cause that seat that’s yes, in Spanish, right,

Alessio: an Italian too,

Simon Hørup Eskildsen: but in full night search. That’s the prefix of maybe a document of like, you know, these are all the reasons I hate Simon, right?

Like this, this is like, that’s a completely different. So that augmentation to like how the human brain works and mapping like data to user is very important, but it’s a lot of features. That feature grind is what we’re firmly on and you will see us just adding to the change log every month, just more and more full tech search features.

Um, so we’re like fully compatible and we see we’re seeing people move from some of the traditional search engine onto Turbo Puffer, um, for that. That’s a big focus of Turbo Puffer this year. The other, the other focus of, of Turbo Puffer this year is just on scale. We’re seeing more and more companies that wanna search basically common crawl level types of data sets.

Um, both internally a companies and externally at, at a time like Cory, like a hundred billion vectors or a hundred billion documents at once. This is tricky and we wanna make it cheaper and we wanna make it faster. Um, that’s a big focus for Turbo Puffer this year. That’s, you know, we just released a NNV three, which we talked about before.

We are working on A-N-N-V-V four and we’re also have planned when we’re gonna do with a and NV five. Right. And then on full Tech search, we’re working on a lot of these features. We’ll be like FTSV three, but it will all roll out incrementally. Um, those are some of the really big features. And then the other thing is, um, our dashboard.

Have any of you ever locked into the Turbo Hover dashboard? It’s not very much there. It almost looks like if, um, a founder two years ago just sat down and wrote enough dashboard that there was at least something there, and then other people just sort of added stuff on for the next two, like the, the following two years, and then at some point SSO and other things to just catch up.

And it may or may not be have what happened, but adding like, I want PHP my admin back. Like, do you, do you guys remember? Like, it was, it was so good. Right? And I think that that like software hardware integration between the, the, the dashboard of the console of the database and the database itself. Um, I’m, I’m really excited for that.

There’s lots of other things, um, that are gonna come out in the next two. Like we talked a bit about some, some pricing and, and things like that, but those would be some of the big hitters. Right Now

swyx: you talk about eras of like turbo profile. I, I just, I have to ask like, yes, there’s the stuff that you’re working on this year, but like I’m sure in your mind you already have the next phase that you’re already thinking about

Simon Hørup Eskildsen: Act three.

swyx: Yes. Act four. Yeah.

Simon Hørup Eskildsen: Act five.

swyx: What I say about that, the candidates, you don’t have to decide. Yeah, but you know,

Simon Hørup Eskildsen: I, I’ll just say that if you wanna build a big database company, the database over time has to implement more or less every quarry plan. Because when you have your data in a database, you expect it to over time, not just search, but also, Hey, I want to aggregate this column, I want to join this data, all of that.

But when you’re a startup, your only moat is really just focus. You have to lay out the vaccine and you have to not get overeager. And I think we’ve seen some of our peers get very overeager and overextend themselves. And what I keep telling the team, I was just having breakfast this morning with our CTO and and chief architect, we were talking about like what we’re most likely to regret at the end of the year is having tried to do too much.

Um, and so Act three candidates could be, you know, a bunch of simpler ola queries, right? It could be, um, lending ourselves a little bit more into, we see some people who wanna do traces and logging and things like that. Some very simple use cases. Could be that, right? It could be maybe some time series.

Some people are trying to do that, right? Like, there’s lots of different things that you can do with turbo puffer, but for now, the, like, if you’re trying, trying to do not search on turbo puffers, the primary use case, you probably shouldn’t, but we see some customers that are like, oh, um, like at some point Cursor moved like 20 terabytes of Postgres data into Turbo Puffer because it’s like, it’s di it’s there, it works.

And these particular query plants we know work well. And so they just moved it all to defer sharding. Um, so we look for patterns like that in what future acts of turban puffer are going to be before firmly doubling down on them. But we wouldn’t, if. Today, if you’re using Turbo Puffer, it should be because search is very important to you.

And then we might do a lot of accelerated queries to that, but that should not be the main reason to go to Turbo Puffer at this point in time.

swyx: Yeah. Uh, you didn’t mention, uh, one thing I was looking for was graph type queries, like graph, database, graph, uh, queries. Can you basically trivially replicate this with what you already have?

Simon Hørup Eskildsen: We see some people doing

swyx: that, right? Because you have parallel queries and it’s It’s the same thing.

Simon Hørup Eskildsen: Exactly. So we see some people doing that, right? Like at the under, like is just a kv, right? And then we expose things on top of it. So we are seeing people do that. And I think, you know, our roadmap is very much just the database that connects AI to a very large amount of data is what the path is to do that in the right order, which is what a good startup is around what is the order to do things in.

Our customers are P 99, and they will tell us what they care most about next. And so some of them are doing graphs now, and if they need more graph database features, they’ll be banking our door and we’ll prioritize accordingly.

swyx: Tea. Okay. Give us the tea. Uh, this, you, you, uh, you kindly gifted us your favorite tea.

This is Yabu Keita Kacha, uh, from the Green Tea Shop. That’s right. Talk about your love of tea.

Simon Hørup Eskildsen: Yeah, we, we were just talking beforehand about, um, um, um. Caffeine, I think, um, and, uh, especially when I’m on a trip like this to San Francisco, I consume a lot of caffeine. Um, but this is my preferred, uh, preferred caffeine.

It’s this green tea. I have an Airtable with 200 teas that I’ve tried over time, over the past, like 15 years, and this one is my favorite. Now, when you drink a tea, um, there’s different, there’s like six different types of tea. I like green tea in particular. I generally prefer Chinese green tea. And I don’t really like Japanese green tea, but this little prefecture somewhere in Japan has specialized in like, they’re like Japanese, but doing it the Chinese way and it’s just phenomenal.

But then the interesting thing about the tea world is that all of the different, um, like you can find this particular tea, there’s probably, you know, hundreds of. Places that sell it, but they all go to a different family right on whatever mountain that they have. These like chameleon, ensis, bush bushes on and this woman, Japanese woman in Toronto from the Green tea shop, um, I don’t know, she’s just like, I has found a really good family.

‘cause that’s the best one. The best time of years to get this is in a few months when they do the spring harvest. Uh, now it’s like kind of old. Um, it’s just like, I love the spring for the fresh tea, so I hope you enjoy it. But it’s not the right time of year.

swyx: It’s out of season. Yeah. I, I, I actually didn’t even know Tea has seasons.

This is unsophisticated, but I, I think it, like, it ties in with like, you know, loving maps and being obsessed and being keen on united in everything that you do. Um, yeah. But. That’s great.

Alessio: Awesome. Well, as we were saying, we have instant hot water at Kernel. So, uh, MET lover can come by any,

Simon Hørup Eskildsen: I I have a little ticket where I bring a, uh, where I bring like a little thermometer to like a little thermoworks thermometer.

Um, last Friday when we do demos, I have this thing where if there’s not enough demos, then I fill the remaining time talking about something completely ridiculous as an incentive for people to actually demo. And last night in time, I spent 20 minutes do, walking through my air table and going through my entire tea travel kit, including the, the, the temperature monitor.

‘cause like Yeah, you’ll show up. There’s only a boiler. You can’t get it to the right. Yeah. You know, you need this at 80 degrees, but anyway. Yeah, sorry.

Alessio: Yeah, we have a, we have electric kettle with the temperature thing at home.

swyx: I would watch this. You should start a company, YouTube, but it doesn’t have anything about search.

It just has and like other brands,

Simon Hørup Eskildsen: I don’t think I could talk, but something that I started doing. Do you, um, do you two know Sam Lambert of, of course, planet Scale? Of

swyx: course.

Simon Hørup Eskildsen: Um,

swyx: very outspoken guy.

Simon Hørup Eskildsen: I love the guy and we just, um, we just last, like last week we just went on X live and just sat and like shut the shit for like an hour and I think we’ll probably do that again.

Yes. We’ll probably come up there. Well, I don’t know what we’ll call it. Maybe P 99 live or the P 99 pod or something like that.

swyx: Um, P pod.

Simon Hørup Eskildsen: P pod.

swyx: Uh, cool. Well thank you so much for your time. I know you have to go, uh, but this is a, a blast and you’re clearly very passionate and charismatic, so, uh, I I bet you’ll get some, uh, P nine nine engineers outta this podcast.

Yeah.

Simon Hørup Eskildsen: Thank you so much for having me. It was a pleasure.
Discussion about this episodeCommentsRestacks
Latent Space: The AI Engineer PodcastThe podcast by and for AI Engineers! In 2025, over 10 million readers and listeners came to Latent Space to hear about news, papers and interviews in Software 3.0.We cover Foundation Models changing every domain in Code Generation, Multimodality, AI Agents, GPU Infra and more, directly from the founders, builders, and thinkers involved in pushing the cutting edge. Striving to give you both the definitive take on the Current Thing down to the first introduction to the tech you'll be using in the next 3 months! We break news and exclusive interviews from OpenAI, Anthropic, Gemini, Meta (Soumith Chintala), Sierra (Bret Taylor), tiny (George Hotz), Databricks/MosaicML (Jon Frankle), Modular (Chris Lattner), Answer.ai (Jeremy Howard), et al. Full show notes always on https://latent.spaceThe podcast by and for AI Engineers! In 2025, over 10 million readers and listeners came to Latent Space to hear about news, papers and interviews in Software 3.0.

We cover Foundation Models changing every domain in Code Generation, Multimodality, AI Agents, GPU Infra and more, directly from the founders, builders, and thinkers involved in pushing the cutting edge. Striving to give you both the definitive take on the Current Thing down to the first introduction to the tech you'll be using in the next 3 months! We break news and exclusive interviews from OpenAI, Anthropic, Gemini, Meta (Soumith Chintala), Sierra (Bret Taylor), tiny (George Hotz), Databricks/MosaicML (Jon Frankle), Modular (Chris Lattner), Answer.ai (Jeremy Howard), et al. 

Full show notes always on https://latent.spaceSubscribeListen onSubstack AppApple PodcastsSpotifyRSS FeedRecent Episodes

Mistral: Voxtral TTS, Forge, Leanstral, & what's next for Mistral 4 — w/ Pavan Kumar Reddy & Guillaume LampleMar 30

🔬Why There Is No "AlphaFold for Materials" — AI for Materials Discovery with Heather KulikMar 24 • Brandon Anderson and RJ Honicky

Dreamer: the Personal Agent OS — David SingletonMar 20

Why Anthropic Thinks AI Should Have Its Own Computer — Felix Rieseberg of Claude Cowork & Claude Code DesktopMar 17

NVIDIA's AI Engineers: Agent Inference at Planetary Scale and "Speed of Light" — Nader Khalil (Brev), Kyle Kranen (Dynamo)Mar 10

Cursor's Third Era: Cloud AgentsMar 6

Every Agent Needs a Box — Aaron Levie, BoxMar 5
## Ready for more?
Subscribe© 2026 Latent.Space · Privacy ∙ Terms ∙ Collection notice

 Start your SubstackGet the appSubstack is the home for great culture
 

 
 
 
 

 
 
 
 
 window._preloads = JSON.parse("{\"isEU\":false,\"language\":\"en\",\"country\":\"US\",\"userLocale\":{\"language\":\"en\",\"region\":\"US\",\"source\":\"default\"},\"base_url\":\"https://www.latent.space\",\"stripe_publishable_key\":\"pk_live_51QfnARLDSWi1i85FBpvw6YxfQHljOpWXw8IKi5qFWEzvW8HvoD8cqTulR9UWguYbYweLvA16P7LN6WZsGdZKrNkE00uGbFaOE3\",\"captcha_site_key\":\"6LeI15YsAAAAAPXyDcvuVqipba_jEFQCjz1PFQoz\",\"pub\":{\"apple_pay_disabled\":false,\"apex_domain\":null,\"author_id\":89230629,\"byline_images_enabled\":true,\"bylines_enabled\":true,\"chartable_token\":null,\"community_enabled\":true,\"copyright\":\"Latent.Space\",\"cover_photo_url\":null,\"created_at\":\"2022-09-12T05:38:09.694Z\",\"custom_domain_optional\":false,\"custom_domain\":\"www.latent.space\",\"default_comment_sort\":\"best_first\",\"default_coupon\":null,\"default_group_coupon\":\"26e3a27d\",\"default_show_guest_bios\":true,\"email_banner_url\":null,\"email_from_name\":\"Latent.Space\",\"email_from\":null,\"embed_tracking_disabled\":false,\"explicit\":false,\"expose_paywall_content_to_search_engines\":true,\"fb_pixel_id\":null,\"fb_site_verification_token\":null,\"flagged_as_spam\":false,\"founding_subscription_benefits\":[\"If we've meaningfully impacted your work/thinking!\"],\"free_subscription_benefits\":[\"All podcasts + public/guest posts\"],\"ga_pixel_id\":null,\"google_site_verification_token\":null,\"google_tag_manager_token\":null,\"hero_image\":null,\"hero_text\":\"The AI Engineer newsletter + Top technical AI podcast. How leading labs build Agents, Models, Infra, & AI for Science. See https://latent.space/about for highlights from Greg Brockman, Andrej Karpathy, George Hotz, Simon Willison, Soumith Chintala et al!\",\"hide_intro_subtitle\":null,\"hide_intro_title\":null,\"hide_podcast_feed_link\":false,\"homepage_type\":\"magaziney\",\"id\":1084089,\"image_thumbnails_always_enabled\":false,\"invite_only\":false,\"hide_podcast_from_pub_listings\":false,\"language\":\"en\",\"logo_url_wide\":\"https://substackcdn.com/image/fetch/$s_!1PJi!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa4fe1182-38af-4a5d-bacc-439c36225e87_5000x1200.png\",\"logo_url\":\"https://substackcdn.com/image/fetch/$s_!DbYa!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F73b0838a-bd14-46a1-801c-b6a2046e5c1e_1130x1130.png\",\"minimum_group_size\":2,\"moderation_enabled\":true,\"name\":\"Latent.Space\",\"paid_subscription_benefits\":[\"Support the podcast and newsletter work we do!\",\"Weekday full AINews!\"],\"parsely_pixel_id\":null,\"chartbeat_domain\":null,\"payments_state\":\"enabled\",\"paywall_free_trial_enabled\":true,\"podcast_art_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/534f41b9-5d2b-49b9-9578-4852473c362f_1400x1400.png\",\"paid_podcast_episode_art_url\":null,\"podcast_byline\":\"Latent.Space\",\"podcast_description\":\"The podcast by and for AI Engineers! In 2025, over 10 million readers and listeners came to Latent Space to hear about news, papers and interviews in Software 3.0.\\n\\nWe cover Foundation Models changing every domain in Code Generation, Multimodality, AI Agents, GPU Infra and more, directly from the founders, builders, and thinkers involved in pushing the cutting edge. Striving to give you both the definitive take on the Current Thing down to the first introduction to the tech you'll be using in the next 3 months! We break news and exclusive interviews from OpenAI, Anthropic, Gemini, Meta (Soumith Chintala), Sierra (Bret Taylor), tiny (George Hotz), Databricks/MosaicML (Jon Frankle), Modular (Chris Lattner), Answer.ai (Jeremy Howard), et al. \\n\\nFull show notes always on https://latent.space\",\"podcast_enabled\":true,\"podcast_feed_url\":null,\"podcast_title\":\"Latent Space: The AI Engineer Podcast\",\"post_preview_limit\":200,\"primary_user_id\":89230629,\"require_clickthrough\":false,\"show_pub_podcast_tab\":false,\"show_recs_on_homepage\":true,\"subdomain\":\"swyx\",\"subscriber_invites\":0,\"support_email\":null,\"theme_var_background_pop\":\"#0068EF\",\"theme_var_color_links\":true,\"theme_var_cover_bg_color\":null,\"trial_end_override\":null,\"twitter_pixel_id\":null,\"type\":\"newsletter\",\"post_reaction_faces_enabled\":true,\"is_personal_mode\":false,\"plans\":[{\"id\":\"yearly80usd\",\"object\":\"plan\",\"active\":true,\"aggregate_usage\":null,\"amount\":8000,\"amount_decimal\":\"8000\",\"billing_scheme\":\"per_unit\",\"created\":1693620604,\"currency\":\"usd\",\"interval\":\"year\",\"interval_count\":1,\"livemode\":true,\"metadata\":{\"substack\":\"yes\"},\"meter\":null,\"nickname\":\"$80 a year\",\"product\":\"prod_OYqzb0iIwest4i\",\"tiers\":null,\"tiers_mode\":null,\"transform_usage\":null,\"trial_period_days\":null,\"usage_type\":\"licensed\",\"currency_options\":{\"aud\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":12000,\"unit_amount_decimal\":\"12000\"},\"brl\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":44500,\"unit_amount_decimal\":\"44500\"},\"cad\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":11000,\"unit_amount_decimal\":\"11000\"},\"chf\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":6500,\"unit_amount_decimal\":\"6500\"},\"dkk\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":51000,\"unit_amount_decimal\":\"51000\"},\"eur\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":7000,\"unit_amount_decimal\":\"7000\"},\"gbp\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":6000,\"unit_amount_decimal\":\"6000\"},\"mxn\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":144500,\"unit_amount_decimal\":\"144500\"},\"nok\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":81000,\"unit_amount_decimal\":\"81000\"},\"nzd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":14000,\"unit_amount_decimal\":\"14000\"},\"pln\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":29000,\"unit_amount_decimal\":\"29000\"},\"sek\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":74000,\"unit_amount_decimal\":\"74000\"},\"usd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":8000,\"unit_amount_decimal\":\"8000\"}}},{\"id\":\"monthly8usd\",\"object\":\"plan\",\"active\":true,\"aggregate_usage\":null,\"amount\":800,\"amount_decimal\":\"800\",\"billing_scheme\":\"per_unit\",\"created\":1693620602,\"currency\":\"usd\",\"interval\":\"month\",\"interval_count\":1,\"livemode\":true,\"metadata\":{\"substack\":\"yes\"},\"meter\":null,\"nickname\":\"$8 a month\",\"product\":\"prod_OYqz6hS4QhIgDK\",\"tiers\":null,\"tiers_mode\":null,\"transform_usage\":null,\"trial_period_days\":null,\"usage_type\":\"licensed\",\"currency_options\":{\"aud\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":1200,\"unit_amount_decimal\":\"1200\"},\"brl\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":4500,\"unit_amount_decimal\":\"4500\"},\"cad\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":1100,\"unit_amount_decimal\":\"1100\"},\"chf\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":700,\"unit_amount_decimal\":\"700\"},\"dkk\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":5500,\"unit_amount_decimal\":\"5500\"},\"eur\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":700,\"unit_amount_decimal\":\"700\"},\"gbp\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":600,\"unit_amount_decimal\":\"600\"},\"mxn\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":14500,\"unit_amount_decimal\":\"14500\"},\"nok\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":8500,\"unit_amount_decimal\":\"8500\"},\"nzd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":1400,\"unit_amount_decimal\":\"1400\"},\"pln\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":2900,\"unit_amount_decimal\":\"2900\"},\"sek\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":7500,\"unit_amount_decimal\":\"7500\"},\"usd\":{\"custom_unit_amount\":null,\"tax_behavior\":\"unspecified\",\"unit_amount\":800,\"unit_amount_decimal\":\"800\"}}},{\"id\":\"founding12300usd\",\"name\":\"founding12300usd\",\"nickname\":\"founding12300usd\",\"active\":true,\"amount\":12300,\"currency\":\"usd\",\"interval\":\"year\",\"interval_count\":1,\"metadata\":{\"substack\":\"yes\",\"founding\":\"yes\",\"no_coupons\":\"yes\",\"short_description\":\"Latent Spacenaut\",\"short_description_english\":\"Latent Spacenaut\",\"minimum\":\"12300\",\"minimum_local\":{\"aud\":18000,\"brl\":64000,\"cad\":17500,\"chf\":10000,\"dkk\":79500,\"eur\":11000,\"gbp\":9500,\"mxn\":220500,\"nok\":119500,\"nzd\":21500,\"pln\":46000,\"sek\":116500,\"usd\":12500}},\"currency_options\":{\"aud\":{\"unit_amount\":18000,\"tax_behavior\":\"unspecified\"},\"brl\":{\"unit_amount\":64000,\"tax_behavior\":\"unspecified\"},\"cad\":{\"unit_amount\":17500,\"tax_behavior\":\"unspecified\"},\"chf\":{\"unit_amount\":10000,\"tax_behavior\":\"unspecified\"},\"dkk\":{\"unit_amount\":79500,\"tax_behavior\":\"unspecified\"},\"eur\":{\"unit_amount\":11000,\"tax_behavior\":\"unspecified\"},\"gbp\":{\"unit_amount\":9500,\"tax_behavior\":\"unspecified\"},\"mxn\":{\"unit_amount\":220500,\"tax_behavior\":\"unspecified\"},\"nok\":{\"unit_amount\":119500,\"tax_behavior\":\"unspecified\"},\"nzd\":{\"unit_amount\":21500,\"tax_behavior\":\"unspecified\"},\"pln\":{\"unit_amount\":46000,\"tax_behavior\":\"unspecified\"},\"sek\":{\"unit_amount\":116500,\"tax_behavior\":\"unspecified\"},\"usd\":{\"unit_amount\":12500,\"tax_behavior\":\"unspecified\"}}}],\"stripe_user_id\":\"acct_1B3pNWKWe8hdGUWL\",\"stripe_country\":\"SG\",\"stripe_publishable_key\":\"pk_live_51B3pNWKWe8hdGUWL8wfT91ugrzbIB6qFqnTzHiUzKR5Sjtm52KIOo0M5yhuAokI02qFay5toW4QfOsJttHMoBivF003gbn4zNC\",\"stripe_platform_account\":\"US\",\"automatic_tax_enabled\":false,\"author_name\":\"Latent.Space\",\"author_handle\":\"swyx\",\"author_photo_url\":\"https://substackcdn.com/image/fetch/$s_!drTb!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdb0f8d45-1eb8-4c02-a120-650d377ee52d_640x640.jpeg\",\"author_bio\":\"Writer, curator, latent space explorer. Main blog: https://swyx.io Devrel/Dev community: https://dx.tips/ Twitter: https://twitter.com/swyx\",\"twitter_screen_name\":\"swyx\",\"has_custom_tos\":false,\"has_custom_privacy\":false,\"theme\":{\"background_pop_color\":\"#9333ea\",\"web_bg_color\":\"#ffffff\",\"cover_bg_color\":\"#ffffff\",\"publication_id\":1084089,\"color_links\":null,\"font_preset_heading\":\"slab\",\"font_preset_body\":\"sans\",\"font_family_headings\":null,\"font_family_body\":null,\"font_family_ui\":null,\"font_size_body_desktop\":null,\"print_secondary\":null,\"custom_css_web\":null,\"custom_css_email\":null,\"home_hero\":\"magaziney\",\"home_posts\":\"custom\",\"home_show_top_posts\":true,\"hide_images_from_list\":false,\"home_hero_alignment\":\"left\",\"home_hero_show_podcast_links\":true,\"default_post_header_variant\":null,\"custom_header\":null,\"custom_footer\":null,\"social_media_links\":null,\"font_options\":null,\"section_template\":null,\"custom_subscribe\":null},\"threads_v2_settings\":{\"photo_replies_enabled\":true,\"first_thread_email_sent_at\":null,\"create_thread_minimum_role\":\"paid\",\"activated_at\":\"2025-09-09T23:28:56.695+00:00\",\"reader_thread_notifications_enabled\":false,\"boost_free_subscriber_chat_preview_enabled\":false,\"push_suppression_enabled\":false},\"default_group_coupon_percent_off\":\"49.00\",\"pause_return_date\":null,\"has_posts\":true,\"has_recommendations\":true,\"first_post_date\":\"2022-09-17T20:35:46.224Z\",\"has_podcast\":true,\"has_free_podcast\":true,\"has_subscriber_only_podcast\":true,\"has_community_content\":true,\"rankingDetail\":\"Thousands of paid subscribers\",\"rankingDetailFreeIncluded\":\"Hundreds of thousands of subscribers\",\"rankingDetailOrderOfMagnitude\":1000,\"rankingDetailFreeIncludedOrderOfMagnitude\":100000,\"rankingDetailFreeSubscriberCount\":\"Over 176,000 subscribers\",\"rankingDetailByLanguage\":{\"ar\":{\"rankingDetail\":\"Thousands of paid subscribers\"},\"ca\":{\"rankingDetail\":\"Milers de subscriptors de pagament\"},\"da\":{\"rankingDetail\":\"Tusindvis af betalte abonnenter\"},\"de\":{\"rankingDetail\":\"Tausende von Paid-Abonnenten\"},\"es\":{\"rankingDetail\":\"Miles de suscriptores de pago\"},\"fr\":{\"rankingDetail\":\"Plusieurs milliers d\u2019abonn\u00E9s payants\"},\"ja\":{\"rankingDetail\":\"\u6570\u5343\u4EBA\u306E\u6709\u6599\u767B\u9332\u8005\"},\"nb\":{\"rankingDetail\":\"Tusenvis av betalende abonnenter\"},\"nl\":{\"rankingDetail\":\"Duizenden betalende abonnees\"},\"pl\":{\"rankingDetail\":\"Tysi\u0105ce p\u0142ac\u0105cych subskrybent\u00F3w\"},\"pt\":{\"rankingDetail\":\"Milhares de subscri\u00E7\u00F5es pagas\"},\"pt-br\":{\"rankingDetail\":\"Milhares de assinantes pagas\"},\"it\":{\"rankingDetail\":\"Migliaia di abbonati a pagamento\"},\"tr\":{\"rankingDetail\":\"Binlerce \u00FCcretli abone\"},\"sv\":{\"rankingDetail\":\"Tusentals betalande prenumeranter\"},\"en\":{\"rankingDetail\":\"Thousands of paid subscribers\"}},\"freeSubscriberCount\":\"176,000\",\"freeSubscriberCountOrderOfMagnitude\":\"176K+\",\"author_bestseller_tier\":1000,\"author_badge\":{\"type\":\"bestseller\",\"tier\":1000},\"disable_monthly_subscriptions\":false,\"disable_annual_subscriptions\":false,\"hide_post_restacks\":false,\"notes_feed_enabled\":false,\"showIntroModule\":false,\"isPortraitLayout\":false,\"last_chat_post_at\":\"2025-09-16T10:15:58.593Z\",\"primary_profile_name\":\"Latent.Space\",\"primary_profile_photo_url\":\"https://substackcdn.com/image/fetch/$s_!drTb!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fdb0f8d45-1eb8-4c02-a120-650d377ee52d_640x640.jpeg\",\"no_follow\":false,\"paywall_chat\":\"free\",\"sections\":[{\"id\":327741,\"created_at\":\"2026-01-23T16:38:15.607Z\",\"updated_at\":\"2026-02-06T00:29:08.963Z\",\"publication_id\":1084089,\"name\":\"AINews: Weekday Roundups\",\"description\":\"Every Weekday - human-curated, AI-summarized news recaps across all of AI Engineering. See https://www.youtube.com/watch?v=IHkyFhU6JEY for how it works\",\"slug\":\"ainews\",\"is_podcast\":false,\"is_live\":true,\"is_default_on\":true,\"sibling_rank\":2,\"port_status\":\"success\",\"logo_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/9a9e98c6-5aeb-461b-b5d0-54d75773e5fa_124x124.png\",\"hide_from_navbar\":false,\"email_from_name\":\"AINews\",\"hide_posts_from_pub_listings\":true,\"email_banner_url\":null,\"cover_photo_url\":null,\"hide_intro_title\":false,\"hide_intro_subtitle\":false,\"ignore_publication_email_settings\":false,\"custom_config\":{},\"pageTheme\":{\"id\":85428,\"publication_id\":1084089,\"section_id\":327741,\"page\":null,\"page_hero\":\"default\",\"page_posts\":\"list\",\"show_podcast_links\":true,\"hero_alignment\":\"left\"},\"showLinks\":[],\"spotifyPodcastSettings\":null,\"podcastSettings\":null,\"podcastPalette\":{\"DarkMuted\":{\"population\":72,\"rgb\":[73,153,137]},\"DarkVibrant\":{\"population\":6013,\"rgb\":[4,100,84]},\"LightMuted\":{\"population\":7,\"rgb\":[142,198,186]},\"LightVibrant\":{\"population\":3,\"rgb\":[166,214,206]},\"Muted\":{\"population\":6,\"rgb\":[92,164,156]},\"Vibrant\":{\"population\":5,\"rgb\":[76,164,146]}},\"spotify_podcast_settings\":null},{\"id\":335089,\"created_at\":\"2026-02-06T00:32:12.973Z\",\"updated_at\":\"2026-02-10T09:26:47.072Z\",\"publication_id\":1084089,\"name\":\"Latent Space: AI for Science\",\"description\":\"a dedicated channel for Latent Space's AI for Science essays that do not get sent to the broader engineering audience \u2014 opt in if high interest in AI for Science!\",\"slug\":\"cience\",\"is_podcast\":false,\"is_live\":true,\"is_default_on\":true,\"sibling_rank\":3,\"port_status\":\"success\",\"logo_url\":null,\"hide_from_navbar\":false,\"email_from_name\":\"Latent Space Science\",\"hide_posts_from_pub_listings\":false,\"email_banner_url\":null,\"cover_photo_url\":null,\"hide_intro_title\":false,\"hide_intro_subtitle\":false,\"ignore_publication_email_settings\":false,\"custom_config\":{},\"pageTheme\":null,\"showLinks\":[],\"spotifyPodcastSettings\":null,\"podcastSettings\":null,\"podcastPalette\":{\"DarkMuted\":{\"population\":72,\"rgb\":[73,153,137]},\"DarkVibrant\":{\"population\":6013,\"rgb\":[4,100,84]},\"LightMuted\":{\"population\":7,\"rgb\":[142,198,186]},\"LightVibrant\":{\"population\":3,\"rgb\":[166,214,206]},\"Muted\":{\"population\":6,\"rgb\":[92,164,156]},\"Vibrant\":{\"population\":5,\"rgb\":[76,164,146]}},\"spotify_podcast_settings\":null}],\"didIdentity\":\"did:plc:es3srknleppmlecmx45g2hoe\",\"multipub_migration\":null,\"navigationBarItems\":[{\"id\":\"ccf2f42a-8937-4639-b19f-c9f4de0e156c\",\"publication_id\":1084089,\"sibling_rank\":0,\"link_title\":null,\"link_url\":null,\"section_id\":null,\"post_id\":null,\"is_hidden\":true,\"standard_key\":\"archive\",\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"b729d56f-08c1-4100-ab1a-205d81648d74\",\"publication_id\":1084089,\"sibling_rank\":1,\"link_title\":null,\"link_url\":null,\"section_id\":null,\"post_id\":null,\"is_hidden\":true,\"standard_key\":\"leaderboard\",\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"8beddb9c-dd08-4f26-8ee0-b070c1512234\",\"publication_id\":1084089,\"sibling_rank\":2,\"link_title\":\"YouTube\",\"link_url\":\"https://www.youtube.com/playlist?list=PLWEAb1SXhjlfkEF_PxzYHonU_v5LPMI8L\",\"section_id\":null,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"32147b98-9d0e-4489-9749-a205af5d5880\",\"publication_id\":1084089,\"sibling_rank\":3,\"link_title\":\"X\",\"link_url\":\"https://x.com/latentspacepod\",\"section_id\":null,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"eb9e689e-85ee-41b2-af34-dd39a2056c7b\",\"publication_id\":1084089,\"sibling_rank\":4,\"link_title\":\"Discord & Meetups\",\"link_url\":\"\",\"section_id\":null,\"post_id\":115665083,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":{\"id\":115665083,\"slug\":\"community\",\"title\":\"Join the Latent.Space Community!\",\"type\":\"page\"},\"section\":null,\"children\":[]},{\"id\":\"338b842e-22f3-4c36-aa92-1c7ebea574d2\",\"publication_id\":1084089,\"sibling_rank\":7,\"link_title\":\"Write for us!\",\"link_url\":\"https://docs.google.com/forms/d/e/1FAIpQLSeHQAgupNkVRgjNfMJG9d7SFTWUytdS6SNCJVkd0SMNMXHHwA/viewform\",\"section_id\":null,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":null,\"children\":[]},{\"id\":\"fc1a55a0-4a35-46e2-8f57-23b3b668d2cc\",\"publication_id\":1084089,\"sibling_rank\":9999,\"link_title\":null,\"link_url\":null,\"section_id\":335089,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":{\"id\":335089,\"slug\":\"cience\",\"name\":\"Latent Space: AI for Science\",\"hide_from_navbar\":false,\"is_podcast\":false,\"logo_url\":null},\"children\":[]},{\"id\":\"d1605792-17ef-44bf-b2a9-42bf42907f5f\",\"publication_id\":1084089,\"sibling_rank\":9999,\"link_title\":null,\"link_url\":null,\"section_id\":327741,\"post_id\":null,\"is_hidden\":null,\"standard_key\":null,\"post_tag_id\":null,\"parent_id\":null,\"is_group\":false,\"postTag\":null,\"post\":null,\"section\":{\"id\":327741,\"slug\":\"ainews\",\"name\":\"AINews: Weekday Roundups\",\"hide_from_navbar\":false,\"is_podcast\":false,\"logo_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/9a9e98c6-5aeb-461b-b5d0-54d75773e5fa_124x124.png\"},\"children\":[]}],\"contributors\":[{\"name\":\"Latent.Space\",\"handle\":\"swyx\",\"role\":\"admin\",\"owner\":true,\"user_id\":89230629,\"photo_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/db0f8d45-1eb8-4c02-a120-650d377ee52d_640x640.jpeg\",\"bio\":\"Writer, curator, latent space explorer. Main blog: https://swyx.io Devrel/Dev community: https://dx.tips/ Twitter: https://twitter.com/swyx\"}],\"threads_v2_enabled\":false,\"viralGiftsConfig\":{\"id\":\"70ab6904-f65b-4d85-9447-df0494958717\",\"publication_id\":1084089,\"enabled\":false,\"gifts_per_user\":5,\"gift_length_months\":1,\"send_extra_gifts\":true,\"message\":\"The AI Engineer newsletter + Top 10 US Tech podcast. Exploring AI UX, Agents, Devtools, Infra, Open Source Models. See https://latent.space/about for highlights from Chris Lattner, Andrej Karpathy, George Hotz, Simon Willison, Emad Mostaque, et al!\",\"created_at\":\"2024-12-19T21:55:43.55283+00:00\",\"updated_at\":\"2024-12-19T21:55:43.55283+00:00\",\"days_til_invite\":14,\"send_emails\":true,\"show_link\":null},\"tier\":2,\"no_index\":false,\"can_set_google_site_verification\":true,\"can_have_sitemap\":true,\"founding_plan_name_english\":\"Latent Spacenaut\",\"bundles\":[],\"base_url\":\"https://www.latent.space\",\"hostname\":\"www.latent.space\",\"is_on_substack\":false,\"show_links\":[{\"id\":35417,\"publication_id\":1084089,\"section_id\":null,\"url\":\"https://podcasts.apple.com/us/podcast/latent-space-the-ai-engineer-podcast/id1674008350\",\"platform\":\"apple_podcasts\"},{\"id\":27113,\"publication_id\":1084089,\"section_id\":null,\"url\":\"https://open.spotify.com/show/7wd4eyLPJvtWnUK1ugH1oi\",\"platform\":\"spotify\"},{\"id\":27114,\"publication_id\":1084089,\"section_id\":null,\"url\":\"https://open.spotify.com/show/7wd4eyLPJvtWnUK1ugH1oi\",\"platform\":\"spotify_for_paid_users\"}],\"spotify_podcast_settings\":{\"id\":7020,\"publication_id\":1084089,\"section_id\":null,\"spotify_access_token\":\"7b7a1a8a-d456-4883-8107-3b04d028beab\",\"spotify_uri\":\"spotify:show:7wd4eyLPJvtWnUK1ugH1oi\",\"spotify_podcast_title\":null,\"created_at\":\"2024-04-17T14:40:50.766Z\",\"updated_at\":\"2024-04-17T14:42:36.242Z\",\"currently_published_on_spotify\":true,\"feed_url_for_spotify\":\"https://api.substack.com/feed/podcast/spotify/7b7a1a8a-d456-4883-8107-3b04d028beab/1084089.rss\",\"spotify_show_url\":\"https://open.spotify.com/show/7wd4eyLPJvtWnUK1ugH1oi\"},\"podcastPalette\":{\"Vibrant\":{\"rgb\":[204,105,26],\"population\":275},\"DarkVibrant\":{\"rgb\":[127,25,90],\"population\":313},\"LightVibrant\":{\"rgb\":[212,111,247],\"population\":333},\"Muted\":{\"rgb\":[152,69,68],\"population\":53},\"DarkMuted\":{\"rgb\":[50,23,49],\"population\":28},\"LightMuted\":{\"rgb\":[109.71710526315789,8.052631578947365,144.94736842105263],\"population\":0}},\"pageThemes\":{\"podcast\":null},\"multiple_pins\":true,\"live_subscriber_counts\":false,\"supports_ip_content_unlock\":false,\"appTheme\":{\"colors\":{\"accent\":{\"name\":\"#9333ea\",\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":126,\"g\":28,\"b\":214,\"a\":1},\"primary_elevated\":{\"r\":126,\"g\":28,\"b\":214,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"bg_hover\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.3},\"dark\":{\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"primary_elevated\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"bg_hover\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.3}}},\"fg\":{\"primary\":{\"r\":0,\"g\":0,\"b\":0,\"a\":0.8},\"secondary\":{\"r\":0,\"g\":0,\"b\":0,\"a\":0.6},\"tertiary\":{\"r\":0,\"g\":0,\"b\":0,\"a\":0.4},\"accent\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"dark\":{\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.9},\"secondary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.6},\"tertiary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.4},\"accent\":{\"r\":174,\"g\":77,\"b\":255,\"a\":1}}},\"bg\":{\"name\":\"#ffffff\",\"hue\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0},\"tint\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0},\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"primary_hover\":{\"r\":250,\"g\":250,\"b\":250,\"a\":1},\"primary_elevated\":{\"r\":250,\"g\":250,\"b\":250,\"a\":1},\"secondary\":{\"r\":238,\"g\":238,\"b\":238,\"a\":1},\"secondary_elevated\":{\"r\":206.90096477355226,\"g\":206.90096477355175,\"b\":206.9009647735519,\"a\":1},\"tertiary\":{\"r\":219,\"g\":219,\"b\":219,\"a\":1},\"quaternary\":{\"r\":182,\"g\":182,\"b\":182,\"a\":1},\"dark\":{\"primary\":{\"r\":22,\"g\":23,\"b\":24,\"a\":1},\"primary_hover\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"primary_elevated\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"secondary\":{\"r\":35,\"g\":37,\"b\":37,\"a\":1},\"secondary_elevated\":{\"r\":41.35899397549579,\"g\":43.405356429195315,\"b\":43.40489285041963,\"a\":1},\"tertiary\":{\"r\":54,\"g\":55,\"b\":55,\"a\":1},\"quaternary\":{\"r\":90,\"g\":91,\"b\":91,\"a\":1}}}},\"cover_image\":{\"url\":\"https://substackcdn.com/image/fetch/$s_!1PJi!,w_1200,h_400,c_pad,f_auto,q_auto:best,fl_progressive:steep,b_auto:border,b_rgb:ffffff/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa4fe1182-38af-4a5d-bacc-439c36225e87_5000x1200.png\",\"height\":400,\"width\":5000}},\"portalAppTheme\":{\"colors\":{\"accent\":{\"name\":\"#9333ea\",\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":135,\"g\":28,\"b\":232,\"a\":1},\"primary_elevated\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":255,\"g\":103,\"b\":25,\"a\":0.2},\"bg_hover\":{\"r\":255,\"g\":103,\"b\":25,\"a\":0.3},\"dark\":{\"primary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"primary_hover\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"primary_elevated\":{\"r\":168,\"g\":71,\"b\":255,\"a\":1},\"secondary\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"contrast\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"bg\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.2},\"bg_hover\":{\"r\":147,\"g\":51,\"b\":234,\"a\":0.3}}},\"fg\":{\"primary\":{\"r\":54,\"g\":55,\"b\":55,\"a\":1},\"secondary\":{\"r\":134,\"g\":135,\"b\":135,\"a\":1},\"tertiary\":{\"r\":146,\"g\":146,\"b\":146,\"a\":1},\"accent\":{\"r\":147,\"g\":51,\"b\":234,\"a\":1},\"dark\":{\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.9},\"secondary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.6},\"tertiary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":0.4},\"accent\":{\"r\":174,\"g\":77,\"b\":255,\"a\":1}}},\"bg\":{\"name\":\"#ffffff\",\"hue\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"tint\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"primary\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"primary_hover\":{\"r\":240,\"g\":240,\"b\":240,\"a\":1},\"primary_elevated\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1},\"secondary\":{\"r\":240,\"g\":240,\"b\":240,\"a\":1},\"secondary_elevated\":{\"r\":240,\"g\":240,\"b\":240,\"a\":1},\"tertiary\":{\"r\":221,\"g\":221,\"b\":221,\"a\":1},\"quaternary\":{\"r\":183,\"g\":183,\"b\":183,\"a\":1},\"dark\":{\"primary\":{\"r\":22,\"g\":23,\"b\":24,\"a\":1},\"primary_hover\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"primary_elevated\":{\"r\":27,\"g\":28,\"b\":29,\"a\":1},\"secondary\":{\"r\":35,\"g\":37,\"b\":37,\"a\":1},\"secondary_elevated\":{\"r\":41.35899397549579,\"g\":43.405356429195315,\"b\":43.40489285041963,\"a\":1},\"tertiary\":{\"r\":54,\"g\":55,\"b\":55,\"a\":1},\"quaternary\":{\"r\":90,\"g\":91,\"b\":91,\"a\":1}}},\"wordmark_bg\":{\"r\":255,\"g\":255,\"b\":255,\"a\":1}},\"fonts\":{\"heading\":\"slab\",\"body\":\"sans\"}},\"logoPalette\":{\"Vibrant\":{\"rgb\":[200,99,28],\"population\":378},\"DarkVibrant\":{\"rgb\":[12,77,99],\"population\":37},\"LightVibrant\":{\"rgb\":[212,110,247],\"population\":348},\"Muted\":{\"rgb\":[152,68,67],\"population\":50},\"DarkMuted\":{\"rgb\":[122,64,142],\"population\":19},\"LightMuted\":{\"rgb\":[109.99999999999996,8,145],\"population\":0}}},\"confirmedLogin\":false,\"hide_intro_popup\":false,\"block_auto_login\":false,\"domainInfo\":{\"isSubstack\":false,\"customDomain\":\"www.latent.space\"},\"experimentFeatures\":{},\"experimentExposures\":{},\"siteConfigs\":{\"score_upsell_email\":\"control\",\"first_chat_email_enabled\":true,\"reader-onboarding-promoted-pub\":737237,\"new_commenter_approval\":false,\"pub_update_opennode_api_key\":false,\"notes_video_max_duration_minutes\":15,\"show_content_label_age_gating_in_feed\":false,\"zendesk_automation_cancellations\":false,\"hide_book_a_meeting_button\":false,\"enable_saved_segments\":false,\"mfa_action_box_enabled\":false,\"publication_max_bylines\":35,\"no_contest_charge_disputes\":false,\"feed_posts_previously_seen_weight\":0.1,\"publication_tabs_reorder\":false,\"comp_expiry_email_new_copy\":\"NONE\",\"free_unlock_required\":false,\"traffic_rule_check_enabled\":false,\"amp_emails_enabled\":false,\"enable_post_summarization\":false,\"live_stream_host_warning_message\":\"\",\"bitcoin_enabled\":false,\"minimum_ios_os_version\":\"17.0.0\",\"show_entire_square_image\":false,\"hide_subscriber_count\":false,\"fit_in_live_stream_player\":false,\"publication_author_display_override\":\"\",\"ios_webview_payments_enabled\":\"control\",\"generate_pdf_tax_report\":false,\"show_generic_post_importer\":false,\"enable_pledges_modal\":true,\"include_pdf_invoice\":false,\"enable_callout_block\":false,\"notes_weight_watch_video\":5,\"enable_react_dashboard\":false,\"meetings_v1\":false,\"enable_videos_page\":false,\"exempt_from_gtm_filter\":false,\"group_sections_and_podcasts_in_menu\":false,\"boost_optin_modal_enabled\":true,\"standards_and_enforcement_features_enabled\":false,\"pub_creation_captcha_behavior\":\"risky_pubs_or_rate_limit\",\"post_blogspot_importer\":false,\"notes_weight_short_item_boost\":0.15,\"enable_high_res_background_uploading\":false,\"pub_tts_override\":\"default\",\"disable_monthly_subscriptions\":false,\"skip_welcome_email\":false,\"chat_reader_thread_notification_default\":false,\"scheduled_pinned_posts\":false,\"disable_redirect_outbound_utm_params\":false,\"reader_gift_referrals_enabled\":true,\"dont_show_guest_byline\":false,\"like_comments_enabled\":true,\"enable_grouped_library\":false,\"temporal_livestream_ended_draft\":true,\"enable_author_note_email_toggle\":false,\"meetings_embed_publication_name\":false,\"fallback_to_archive_search_on_section_pages\":false,\"livekit_track_egress_custom_base_url\":\"http://livekit-egress-custom-recorder-participant-test.s3-website-us-east-1.amazonaws.com\",\"people_you_may_know_algorithm\":\"experiment\",\"welcome_screen_blurb_override\":\"\",\"notes_weight_low_impression_boost\":0.3,\"like_posts_enabled\":true,\"feed_promoted_video_boost\":1.5,\"twitter_player_card_enabled\":true,\"subscribe_bypass_preact_router\":false,\"feed_promoted_user\":false,\"show_note_stats_for_all_notes\":false,\"section_specific_csv_imports_enabled\":false,\"disable_podcast_feed_description_cta\":false,\"bypass_profile_substack_logo_detection\":false,\"use_preloaded_player_sources\":false,\"enable_tiktok_oauth\":false,\"list_pruning_enabled\":false,\"facebook_connect\":false,\"opt_in_to_sections_during_subscribe\":false,\"dpn_weight_share\":2,\"underlined_colored_links\":false,\"enable_efficient_digest_embed\":false,\"extract_stripe_receipt_url\":false,\"enable_aligned_images\":false,\"max_image_upload_mb\":64,\"threads_suggested_ios_version\":null,\"pledges_disabled\":false,\"threads_minimum_ios_version\":812,\"hide_podcast_email_setup_link\":false,\"subscribe_captcha_behavior\":\"default\",\"publication_ban_sample_rate\":0,\"enable_note_polls\":false,\"ios_enable_publication_activity_tab\":false,\"custom_themes_substack_subscribe_modal\":false,\"ios_post_share_assets_screenshot_trigger\":\"control\",\"opt_in_to_sections_during_subscribe_include_main_pub_newsletter\":false,\"continue_support_cta_in_newsletter_emails\":false,\"bloomberg_syndication_enabled\":false,\"welcome_page_app_button\":true,\"lists_enabled\":false,\"adhoc_email_batch_delay_ms\":0,\"generated_database_maintenance_mode\":false,\"allow_document_freeze\":false,\"test_age_gate_user\":false,\"podcast_main_feed_is_firehose\":false,\"pub_app_incentive_gift\":\"\",\"no_embed_redirect\":false,\"customized_email_from_name_for_new_follow_emails\":\"treatment\",\"spotify_open_access_sandbox_mode\":false,\"enable_founding_iap_plans\":true,\"fullstory_enabled\":false,\"chat_reply_poll_interval\":3,\"dpn_weight_follow_or_subscribe\":3,\"thefp_enable_email_upsell_banner\":false,\"android_restore_feed_scroll_position\":\"experiment\",\"force_pub_links_to_use_subdomain\":false,\"always_show_cookie_banner\":false,\"hide_media_download_option\":false,\"hide_post_restacks\":false,\"feed_item_source_debug_mode\":false,\"ios_subscription_bar_live_polling_enabled\":true,\"enable_user_status_ui\":false,\"publication_homepage_title_display_override\":\"\",\"post_preview_highlight_byline\":false,\"4k_video\":false,\"enable_islands_section_intent_screen\":false,\"post_metering_enabled\":false,\"notifications_disabled\":\"\",\"cross_post_notification_threshold\":1000,\"facebook_connect_prod_app\":true,\"force_into_pymk_ranking\":false,\"minimum_android_version\":756,\"live_stream_krisp_noise_suppression_enabled\":false,\"enable_transcription_translations\":false,\"nav_group_items\":false,\"use_og_image_as_twitter_image_for_post_previews\":false,\"always_use_podcast_channel_art_as_episode_art_in_rss\":false,\"enable_sponsorship_perks\":false,\"seo_tier_override\":\"NONE\",\"editor_role_enabled\":false,\"no_follow_links\":false,\"publisher_api_enabled\":false,\"zendesk_support_priority\":\"default\",\"enable_post_clips_stats\":false,\"enable_subscriber_referrals_awards\":true,\"ios_profile_themes_feed_permalink_enabled\":false,\"include_thumbnail_landscape_layouts\":true,\"use_publication_language_for_transcription\":false,\"show_substack_funded_gifts_tooltip\":true,\"disable_ai_transcription\":false,\"thread_permalink_preview_min_ios_version\":4192,\"live_stream_founding_audience_enabled\":false,\"android_toggle_on_website_enabled\":false,\"internal_android_enable_post_editor\":false,\"enable_pencraft_sandbox_access\":false,\"updated_inbox_ui\":false,\"live_stream_creation_enabled\":true,\"disable_card_element_in_europe\":false,\"web_growth_item_promotion_threshold\":0,\"bundle_subscribe_enabled\":false,\"enable_web_typing_indicators\":false,\"web_vitals_sample_rate\":0,\"allow_live_stream_auto_takedown\":\"true\",\"mobile_publication_attachments_enabled\":false,\"ios_post_dynamic_title_size\":false,\"ios_enable_live_stream_highlight_trailer_toggle\":false,\"ai_image_generation_enabled\":true,\"disable_personal_substack_initialization\":false,\"section_specific_welcome_pages\":false,\"local_payment_methods\":\"control\",\"publisher_api_cancel_comp\":false,\"posts_in_rss_feed\":20,\"post_rec_endpoint\":\"\",\"publisher_dashboard_section_selector\":false,\"reader_surveys_platform_question_order\":\"36,1,4,2,3,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35\",\"developer_api_enabled\":false,\"login_guard_app_link_in_email\":true,\"community_moderators_enabled\":false,\"monthly_sub_is_one_off\":false,\"unread_notes_activity_digest\":\"control\",\"display_cookie_settings\":false,\"welcome_page_query_params\":false,\"enable_free_podcast_urls\":false,\"email_post_stats_v2\":false,\"comp_expiry_emails_disabled\":false,\"enable_description_on_polls\":false,\"use_microlink_for_instagram_embeds\":false,\"post_notification_batch_delay_ms\":30000,\"free_signup_confirmation_behavior\":\"with_email_validation\",\"ios_post_stats_for_admins\":false,\"enable_livestream_branding\":true,\"use_livestream_post_media_composition\":true,\"section_specific_preambles\":false,\"pub_export_temp_disable\":false,\"show_menu_on_posts\":false,\"android_reset_backstack_after_timeout\":false,\"ios_post_subscribe_web_routing\":true,\"ios_writer_stats_public_launch_v2\":false,\"min_size_for_phishing_check\":1,\"enable_android_post_stats\":false,\"ios_chat_revamp_enabled\":false,\"app_onboarding_survey_email\":false,\"republishing_enabled\":false,\"app_mode\":false,\"show_phone_banner\":true,\"live_stream_video_enhancer\":\"internal\",\"minimum_ios_version\":2200,\"enable_author_pages\":false,\"enable_decagon_chat\":true,\"first_month_upsell\":\"control\",\"enable_subscriber_tags\":false,\"new_user_checklist_enabled\":\"use_follower_count\",\"ios_feed_note_status_polling_enabled\":false,\"latex_upgraded_inline\":false,\"show_attached_profile_for_pub_setting\":false,\"ios_feed_subscribe_upsell\":\"experiment\",\"rss_verification_code\":\"\",\"notification_post_emails\":\"experiment\",\"notes_weight_follow\":3.8,\"chat_suppress_contributor_push_option_enabled\":false,\"use_og_image_asset_variant\":\"\",\"export_hooks_enabled\":false,\"audio_encoding_bitrate\":null,\"bestseller_pub_override\":false,\"extra_seats_coupon_type\":false,\"post_subdomain_universal_links\":false,\"post_import_max_file_size\":26214400,\"feed_promoted_video_publication\":false,\"livekit_reconnect_slate_url\":\"https://mux-livestream-assets.s3.us-east-1.amazonaws.com/custom-disconnect-slate-tall.png\",\"exclude_from_pymk_suggestions\":false,\"publication_ranking_variant\":\"experiment\",\"disable_annual_subscriptions\":false,\"hack_jane_manchun_wong\":true,\"android_enable_auto_gain_control\":true,\"enable_android_dms\":false,\"allow_coupons_on_upgrade\":false,\"test_au_age_gate_user\":false,\"pub_auto_moderation_enabled\":false,\"disable_live_stream_ai_trimming_by_default\":false,\"disable_deletion\":false,\"ios_default_coupon_enabled\":false,\"notes_weight_read_post\":5,\"notes_weight_reply\":3,\"livekit_egress_custom_base_url\":\"http://livekit-egress-custom-recorder.s3-website-us-east-1.amazonaws.com\",\"clip_focused_video_upload_flow\":false,\"live_stream_max_guest_users\":2,\"android_upgrade_alert_dialog_reincarnated\":true,\"enable_video_seo_data\":false,\"can_reimport_unsubscribed_users_with_2x_optin\":false,\"feed_posts_weight_subscribed\":0,\"founding_upgrade_during_gift_disabled\":false,\"live_event_mixin\":\"\",\"review_incoming_email\":\"default\",\"media_feed_subscribed_posts_weight\":0.5,\"enable_founding_gifts\":false,\"enable_creator_agency_pages\":false,\"enable_sponsorship_campaigns\":false,\"thread_permalink_preview_min_android_version\":2037,\"enable_creator_earnings\":true,\"thefp_enable_embed_media_links\":false,\"thumbnail_selection_max_frames\":300,\"sort_modal_search_results\":false,\"default_thumbnail_time\":10,\"pub_ranking_weight_retained_engagement\":1,\"load_test_unichat\":false,\"notes_read_post_baseline\":0,\"live_stream_head_alignment_guide\":false,\"show_open_post_as_pdf_button\":false,\"free_press_combo_subscribe_flow_enabled\":false,\"android_note_auto_share_assets\":\"control\",\"pub_ranking_weight_immediate_engagement\":0.5,\"enable_portal_feed_post_comments\":false,\"gifts_from_substack_feature_available\":true,\"disable_ai_clips\":false,\"enable_elevenlabs_voiceovers\":false,\"use_web_livestream_thumbnail_editor\":true,\"show_simple_post_editor\":false,\"instacart_integration_enabled\":false,\"enable_publication_podcasts_page\":false,\"android_profile_share_assets_experiment\":\"treatment\",\"use_advanced_fonts\":false,\"growth_sources_all_time\":true,\"ios_note_composer_settings_enabled\":false,\"android_v2_post_video_player_enabled\":false,\"enable_direct_message_request_bypass\":false,\"enable_apple_news_sync\":false,\"live_stream_in_trending_topic_overrides\":\"\",\"media_feed_prepend_inbox_limit\":30,\"free_press_newsletter_promo_enabled\":false,\"enable_ios_livestream_stats\":true,\"disable_live_stream_reactions\":false,\"feed_posts_weight_negative\":2.5,\"instacart_partner_id\":\"\",\"clip_generation_3rd_party_vendor\":\"internal\",\"ios_onboarding_collapsable_categories_with_sentiment\":\"experiment\",\"welcome_page_no_opt_out\":false,\"android_feed_menu_copy_link_experiment\":\"experiment\",\"notes_weight_negative\":1,\"ios_discover_tab_min_installed_date\":\"2025-06-09T16:56:58+0000\",\"notes_weight_click_see_more\":2,\"edit_profile_theme_colors\":false,\"notes_weight_like\":2.4,\"disable_clipping_for_readers\":false,\"feed_posts_weight_share\":6,\"android_creator_earnings_enabled\":true,\"feed_posts_weight_reply\":3,\"feed_posts_weight_like\":1.5,\"feed_posts_weight_save\":3,\"enable_press_kit_preview_modal\":false,\"dpn_weight_tap_clickbait_penalty\":0.5,\"feed_posts_weight_sign_up\":4,\"live_stream_video_degradation_preference\":\"maintainFramerate\",\"enable_high_follower_dm\":true,\"pause_app_badges\":false,\"android_enable_publication_activity_tab\":false,\"ios_hide_author_in_share_sheet\":\"control\",\"profile_feed_expanded_inventory\":false,\"phone_verification_fallback_to_twilio\":false,\"android_onboarding_suggestions_hero_text\":\"experiment\",\"livekit_mux_latency_mode\":\"low\",\"feed_juiced_user\":0,\"universal_feed_translator_experiment\":\"control\",\"notes_click_see_more_baseline\":0.35,\"enable_polymarket_expandable_embeds\":true,\"publication_onboarding_weight_std_dev\":0,\"can_see_fast_subscriber_counts\":true,\"android_enable_user_status_ui\":false,\"use_advanced_commerce_api_for_iap\":false,\"skip_free_preview_language_in_podcast_notes\":false,\"larger_wordmark_on_publication_homepage\":false,\"video_editor_full_screen\":false,\"enable_mobile_stats_for_admins\":false,\"ios_profile_themes_note_composer_enabled\":false,\"enable_persona_sandbox_environment\":false,\"notes_weight_click_item\":3,\"notes_weight_long_visit\":1,\"bypass_single_unlock_token_limit\":false,\"notes_watch_video_baseline\":0.08,\"enable_free_trial_subscription_ios\":true,\"polymarket_minimum_confidence_for_trending_topics\":100,\"add_section_and_tag_metadata\":false,\"daily_promoted_notes_enabled\":true,\"enable_islands_cms\":false,\"enable_livestream_combined_stats\":false,\"ios_social_subgroups_enabled\":false,\"chartbeat_video_enabled\":false,\"enable_drip_campaigns\":false,\"adhoc_email_batch_size\":5000,\"ios_offline_mode_enabled\":false,\"enable_pinned_portals\":false,\"post_management_search_engine\":\"elasticsearch\",\"new_bestseller_leaderboard_feed_item_enabled\":false,\"feed_main_disabled\":false,\"enable_account_settings_revamp\":false,\"allowed_email_domains\":\"one\",\"thefp_enable_fp_recirc_block\":false,\"top_search_variant\":\"control\",\"enable_debug_logs_ios\":false,\"show_pub_content_on_profile_for_pub_id\":0,\"show_pub_content_on_profile\":false,\"livekit_track_egress\":true,\"video_tab_mixture_pattern\":\"npnnnn\",\"enable_theme_contexts\":false,\"onboarding_suggestions_search\":\"experiment\",\"feed_tuner_enabled\":false,\"livekit_mux_latency_mode_rtmp\":\"low\",\"draft_notes_enabled\":true,\"fcm_high_priority\":false,\"enable_drop_caps\":true,\"search_category_variant\":\"control\",\"highlighted_code_block_enabled\":true,\"dpn_weight_tap_bonus_subscribed\":0,\"iap_announcement_blog_url\":\"\",\"android_onboarding_progress_persistence\":\"control\",\"ios_livestream_feedback\":false,\"founding_plan_upgrade_warning\":false,\"dpn_weight_like\":3,\"dpn_weight_short_session\":1,\"ios_enable_custom_thumbnail_generation\":true,\"ios_mediaplayer_reply_bar_v2\":false,\"android_view_post_share_assets_employees_only\":false,\"stripe_link_in_payment_element_v3\":\"treatment\",\"enable_notification_email_batching\":true,\"notes_weight_follow_boost\":10,\"profile_portal_theme\":false,\"ios_hide_portal_tab_bar\":false,\"follow_upsell_rollout_percentage\":30,\"android_activity_item_sharing_experiment\":\"control\",\"live_stream_invite_ttl_seconds\":900000,\"include_founding_plans_coupon_option\":false,\"thefp_enable_cancellation_discount_offer\":false,\"dpn_weight_reply\":2,\"thefp_free_trial_experiment\":\"treatment\",\"android_enable_edit_profile_theme\":false,\"twitter_api_enabled\":true,\"dpn_weight_follow\":3,\"thumbnail_selection_engine\":\"openai\",\"enable_adhoc_email_batching\":0,\"notes_weight_author_low_impression_boost\":0.2,\"disable_audio_enhancement\":false,\"pub_search_variant\":\"control\",\"ignore_video_in_notes_length_limit\":false,\"web_show_scores_on_sports_tab\":false,\"notes_weight_click_share\":3,\"allow_long_videos\":true,\"feed_posts_weight_long_click\":15,\"dpn_score_threshold\":0,\"thefp_annual_subscription_promotion\":\"treatment\",\"dpn_weight_follow_bonus\":0.5,\"enable_fullscreen_post_live_end_screen\":false,\"use_intro_clip_and_branded_intro_by_default\":false,\"use_enhanced_video_embed_player\":true,\"community_profile_activity_feed\":false,\"android_reader_share_assets_3\":\"control\",\"email_change_minimum_bot_score\":0,\"mobile_age_verification_learn_more_link\":\"https://on.substack.com/p/our-position-on-the-online-safety\",\"enable_viewing_all_livestream_viewers\":false,\"web_suggested_search_route_recent_search\":\"control\",\"enable_clip_prompt_variant_filtering\":true,\"chartbeat_enabled\":false,\"dpn_weight_disable\":10,\"dpn_ranking_enabled\":true,\"reply_flags_enabled\":true,\"enable_custom_email_css\":false,\"dpn_model_variant\":\"experiment\",\"android_og_tag_post_sharing_experiment\":\"control\",\"platform_search_variant\":\"control\",\"enable_apple_podcast_auto_publish\":false,\"linkedin_profile_search_enabled\":false,\"ios_better_top_search_prompt_in_global_search\":\"control\",\"retire_i18n_marketing_pages\":true,\"publication_has_own_app\":false,\"suggested_minimum_ios_version\":0,\"dpn_weight_open\":2.5,\"ios_pogs_stories\":\"experiment\",\"enable_notes_admins\":false,\"trending_topics_module_long_term_experiment\":\"control\",\"enable_suggested_searches\":true,\"enable_subscription_notification_email_batching\":true,\"android_synchronous_push_notif_handling\":\"control\",\"thumbnail_selection_skip_desktop_streams\":false,\"a24_redemption_link\":\"\",\"dpn_weight_tap\":2.5,\"ios_live_stream_auto_gain_enabled\":true,\"dpn_weight_restack\":2,\"dpn_weight_negative\":40,\"enable_publication_tts_player\":false,\"enable_ios_post_page_themes\":false,\"session_version_invalidation_enabled\":false,\"search_retrieval_variant\":\"experiment\",\"galleried_feed_attachments\":true,\"web_post_attachment_fallback\":\"treatment\",\"enable_live_stream_thumbnail_treatment_validation\":true,\"forced_featured_topic_id\":\"\",\"ios_audio_captions_disabled\":false,\"reader_onboarding_modal_v2_vs_page\":\"experiment\",\"related_posts_enabled\":false,\"use_progressive_editor_rollout\":true,\"ios_live_stream_pip_dismiss_v4\":\"control\",\"reply_rate_limit_max_distinct_users_daily\":110,\"galleried_feed_attachments_in_composer\":false,\"android_rank_share_destinations_experiment\":\"control\",\"publisher_banner\":\"\",\"suggested_search_metadata_web_ui\":true,\"mobile_user_attachments_enabled\":false,\"enable_library_compaction\":true,\"ios_founding_upgrade_button_in_portals_v2\":\"control\",\"enable_ios_chat_themes\":false,\"feed_weight_language_mismatch_penalty\":0.6,\"default_orange_quote_experiment\":\"control\",\"enable_high_res_recording_workflow\":false,\"community_activity_feed_author_to_community_content_ratio\":0.5,\"enable_sponsorship_profile\":false,\"ios_onboarding_multiple_notification_asks\":\"control\",\"ios_founding_upgrade_button_in_portals\":\"control\",\"ios_mid_read_post_reminder_v2\":\"treatment\",\"ios_inline_upgrade_on_feed_items\":\"control\",\"reply_rate_limit_max_distinct_users_monthly\":600,\"show_branded_intro_setting\":false,\"desktop_live_stream_screen_share_audio_enabled\":false,\"search_posts_use_top_search\":false,\"ios_inbox_observe_by_key\":true,\"profile_photo_upsell_modal\":\"treatment\",\"enable_high_res_background_uploading_session_recovery\":false,\"portal_post_style\":\"control\",\"search_ranker_variant\":\"experiment\",\"dpn_weight_long_session\":2,\"use_custom_header_by_default\":false,\"ios_listen_tab\":false,\"android_composer_modes_vs_attachments\":\"control\",\"activity_item_ranking_variant\":\"experiment\",\"android_polymarket_embed_search\":false,\"ios_onboarding_new_user_survey\":\"experiment\",\"android_post_like_share_nudge\":\"treatment\",\"android_post_bottom_share_experiment\":\"treatment\",\"enable_post_templates\":true,\"use_thumbnail_selection_sentiment_matching\":true,\"skip_adhoc_email_sends\":false,\"android_enable_draft_notes\":true,\"permalink_reply_ranking_variant\":\"experiment\",\"desktop_live_stream_participant_labels\":false,\"allow_feed_category_filtering\":false,\"enable_livestream_screenshare_detection\":true,\"private_live_streaming_enabled\":true,\"android_scheduled_notes_enabled\":true,\"private_live_streaming_banner_enabled\":false,\"portal_ranking_variant\":\"experiment\",\"desktop_live_stream_safe_framing\":0.8,\"android_onboarding_swipeable_cards\":\"control\",\"enable_note_scheduling\":true,\"ios_limit_related_notes_in_permalink\":\"control\"},\"publicationSettings\":{\"block_ai_crawlers\":false,\"credit_token_enabled\":true,\"custom_tos_and_privacy\":false,\"did_identity\":\"did:plc:es3srknleppmlecmx45g2hoe\",\"disable_optimistic_bank_payments\":false,\"display_welcome_page_details\":true,\"enable_meetings\":false,\"payment_pledges_enabled\":true,\"enable_drop_caps\":false,\"enable_post_page_conversion\":false,\"enable_prev_next_nav\":true,\"enable_restacking\":true,\"gifts_from_substack_disabled\":false,\"google_analytics_4_token\":null,\"group_sections_and_podcasts_in_menu_enabled\":false,\"live_stream_homepage_visibility\":\"contributorsAndAdmins\",\"live_stream_homepage_style\":\"banner\",\"medium_length_description\":\"The AI Engineer newsletter + Top 10 US Tech podcast + Community. Interviews, Essays and Guides on frontier LLMs, AI Infra, Agents, Devtools, UX, Open Models. See https://latent.space/about for highlights from Chris Lattner, Andrej Karpathy, George Hotz, Simon Willison, Soumith Chintala, et al!\",\"notes_feed_enabled\":false,\"paywall_unlock_tokens\":false,\"post_preview_crop_gravity\":\"auto\",\"post_preview_radius\":\"xs\",\"reader_referrals_enabled\":true,\"reader_referrals_leaderboard_enabled\":true,\"seen_coming_soon_explainer\":false,\"seen_google_analytics_migration_modal\":false,\"local_currency_modal_seen\":true,\"local_payment_methods_modal_seen\":true,\"twitter_pixel_signup_event_id\":null,\"twitter_pixel_subscribe_event_id\":null,\"use_local_currency\":true,\"welcome_page_opt_out_text\":\"No thanks\",\"cookie_settings\":\"\",\"show_restacks_below_posts\":true,\"holiday_gifting_post_header\":true,\"homepage_message_text\":\"\",\"homepage_message_link\":\"\",\"about_us_author_ids\":\"\",\"archived_section_ids\":\"\",\"column_section_ids\":\"\",\"fp_primary_column_section_ids\":\"\",\"event_section_ids\":\"\",\"podcasts_metadata\":\"\",\"video_section_ids\":\"\",\"post_metering_enabled\":false},\"publicationUserSettings\":null,\"userSettings\":{\"user_id\":null,\"activity_likes_enabled\":true,\"dashboard_nav_refresh_enabled\":false,\"hasDismissedSectionToNewsletterRename\":false,\"is_guest_post_enabled\":true,\"feed_web_nux_seen_at\":null,\"has_seen_select_to_restack_tooltip_nux\":false,\"invite_friends_nux_dismissed_at\":null,\"suggestions_feed_item_last_shown_at\":null,\"has_seen_select_to_restack_modal\":false,\"last_notification_alert_shown_at\":null,\"disable_reply_hiding\":false,\"newest_seen_chat_item_published_at\":null,\"explicitContentEnabled\":false,\"contactMatchingEnabled\":false,\"messageRequestLevel\":\"everyone\",\"liveStreamAcceptableInviteLevel\":\"everyone\",\"liveStreamAcceptableChatLevel\":\"everyone\",\"creditTokensTreatmentExposed\":false,\"appBadgeIncludesChat\":false,\"autoPlayVideo\":true,\"smart_delivery_enabled\":false,\"chatbotTermsLastAcceptedAt\":null,\"has_seen_notes_post_app_upsell\":false,\"substack_summer_nux_dismissed_at\":null,\"first_note_id\":null,\"show_concurrent_live_stream_viewers\":false,\"has_dismissed_fp_download_pdf_nux\":false,\"edit_profile_feed_item_dismissed_at\":null,\"mobile_permalink_app_upsell_seen_at\":null,\"new_user_checklist_enabled\":false,\"new_user_follow_subscribe_prompt_dismissed_at\":null,\"has_seen_youtube_shorts_auto_publish_announcement\":false,\"has_seen_publish_youtube_connect_upsell\":false,\"notificationQualityFilterEnabled\":true,\"hasSeenOnboardingNewslettersScreen\":false,\"bestsellerBadgeEnabled\":true,\"hasSelfIdentifiedAsCreator\":false,\"autoTranslateEnabled\":true,\"autoTranslateBlocklist\":[]},\"subscriberCountDetails\":\"hundreds of thousands of subscribers\",\"mux_env_key\":\"u42pci814i6011qg3segrcpp9\",\"persona_environment_id\":\"env_o1Lbk4JhpY4PmvNkwaBdYwe5Fzkt\",\"sentry_environment\":\"production\",\"launchWelcomePage\":false,\"pendingInviteForActiveLiveStream\":null,\"isEligibleForLiveStreamCreation\":true,\"webviewPlatform\":null,\"noIndex\":false,\"post\":{\"audience\":\"everyone\",\"audience_before_archived\":null,\"canonical_url\":\"https://www.latent.space/p/turbopuffer\",\"default_comment_sort\":null,\"editor_v2\":false,\"exempt_from_archive_paywall\":false,\"free_unlock_required\":false,\"id\":190777516,\"podcast_art_url\":null,\"podcast_duration\":3632.4048,\"podcast_preview_upload_id\":null,\"podcast_upload_id\":\"f7a9aba8-7fe1-4ab1-a5c6-c6a9d16344dc\",\"podcast_url\":\"https://api.substack.com/api/v1/audio/upload/f7a9aba8-7fe1-4ab1-a5c6-c6a9d16344dc/src\",\"post_date\":\"2026-03-12T22:56:01.777Z\",\"updated_at\":\"2026-03-12T22:57:24.462Z\",\"publication_id\":1084089,\"search_engine_description\":null,\"search_engine_title\":null,\"section_id\":null,\"should_send_free_preview\":false,\"show_guest_bios\":true,\"slug\":\"turbopuffer\",\"social_title\":null,\"subtitle\":\"\",\"teaser_post_eligible\":true,\"title\":\"Retrieval After RAG: Hybrid Search, Agents, and Database Design \u2014 Simon H\u00F8rup Eskildsen of Turbopuffer\",\"type\":\"podcast\",\"video_upload_id\":null,\"write_comment_permissions\":\"everyone\",\"meter_type\":\"none\",\"live_stream_id\":null,\"is_published\":true,\"restacks\":2,\"reactions\":{\"\u2764\":27},\"top_exclusions\":[],\"pins\":[],\"section_pins\":[],\"has_shareable_clips\":false,\"previous_post_slug\":\"nvidia-brev-dynamo\",\"next_post_slug\":\"felix-anthropic\",\"cover_image\":\"https://substack-video.s3.amazonaws.com/video_upload/post/190777516/f7a9aba8-7fe1-4ab1-a5c6-c6a9d16344dc/transcoded-1773352613.png\",\"cover_image_is_square\":false,\"cover_image_is_explicit\":false,\"podcast_episode_image_url\":\"https://substack-post-media.s3.amazonaws.com/public/images/534f41b9-5d2b-49b9-9578-4852473c362f_1400x1400.png\",\"podcast_episode_image_info\":{\"url\":\"https://substack-post-media.s3.amazonaws.com/public/images/534f41b9-5d2b-49b9-9578-4852473c362f_1400x1400.png\",\"isDefaultArt\":false,\"isDefault\":false},\"videoUpload\":null,\"podcastFields\":{\"post_id\":190777516,\"podcast_episode_number\":null,\"podcast_season_number\":null,\"podcast_episode_type\":null,\"should_syndicate_to_other_feed\":null,\"syndicate_to_section_id\":null,\"hide_from_feed\":false,\"free_podcast_url\":null,\"free_podcast_duration\":null},\"podcastUpload\":{\"id\":\"f7a9aba8-7fe1-4ab1-a5c6-c6a9d16344dc\",\"name\":\"final mix LSP- EP Turbopuffer.mp3\",\"created_at\":\"2026-03-12T21:52:34.210Z\",\"uploaded_at\":\"2026-03-12T21:52:38.106Z\",\"publication_id\":1084089,\"state\":\"transcoded\",\"post_id\":190777516,\"user_id\":46786399,\"duration\":3632.4048,\"height\":null,\"width\":null,\"thumbnail_id\":1773352613,\"preview_start\":null,\"preview_duration\":null,\"media_type\":\"audio\",\"primary_file_size\":58118940,\"is_mux\":false,\"mux_asset_id\":null,\"mux_playback_id\":null,\"mux_preview_asset_id\":null,\"mux_preview_playback_id\":null,\"mux_rendition_quality\":null,\"mux_preview_rendition_quality\":null,\"explicit\":false,\"copyright_infringement\":null,\"src_media_upload_id\":null,\"live_stream_id\":null,\"transcription\":{\"media_upload_id\":\"f7a9aba8-7fe1-4ab1-a5c6-c6a9d16344dc\",\"created_at\":\"2026-03-12T21:53:32.824Z\",\"requested_by\":46786399,\"status\":\"transcribed\",\"modal_call_id\":\"fc-01KKJ0MSHXYK1K0NHNGX2BNECF\",\"approved_at\":\"2026-03-12T21:57:03.469Z\",\"transcript_url\":\"s3://substack-video/video_upload/post/190777516/f7a9aba8-7fe1-4ab1-a5c6-c6a9d16344dc/1773352418/transcription.json\",\"attention_vocab\":null,\"speaker_map\":null,\"captions_map\":{\"en\":{\"url\":\"s3://substack-video/video_upload/post/190777516/f7a9aba8-7fe1-4ab1-a5c6-c6a9d16344dc/1773352418/en.vtt\",\"language\":\"en\",\"original\":true}},\"cdn_url\":\"https://substackcdn.com/video_upload/post/190777516/f7a9aba8-7fe1-4ab1-a5c6-c6a9d16344dc/1773352418/transcription.json?Expires=1775560045&Key-Pair-Id=APKAIVDA3NPSMPSPESQQ&Signature=a4I6XUDOFyuqmOnfTx3lOgyXQxSqqHjDju6-nufM~sIscu6imoLkaRVYw1FiUpM2NdCvrVT~rTzvzQZPOnsAklg7XeqKsq7mFcRbapuZVbaSV9VMc6x393J~qVSj62c8QnNYnFDWpbBdMTrVfq9i6wWrQcf8GE8u0VcAe5xfxHidmoZ4pVJl4bxXp5soz1kL9tgBvivPmnX36loObPIdED-7fZGfmH8-6eElhwZdwRB8G71vQiTdS7lUWr3mh3-l0y2tla1CTpWWohSIu1TZIy55MEuK-DUs29cgJedHJffBTzrtmSIh0sM7IIylDjVxlVDdPtm-alIba7eQOTqBAg__\",\"cdn_unaligned_url\":\"https://substackcdn.com/video_upload/post/190777516/f7a9aba8-7fe1-4ab1-a5c6-c6a9d16344dc/1773352418/unaligned_transcription.json?Expires=1775560045&Key-Pair-Id=APKAIVDA3NPSMPSPESQQ&Signature=SmPPf-DSZ~3vVFqjSNiLj9zXeEoYp2XRRHRYPVMZbc3KYbqszZHwGmIbD38k6Uq-baZxXoLgsuBX-EEw6GOEOVqSBjkMF-pPC3~wEQEc0p3ZBfrWpUWJ34USQkBsE-8obQ8iRUPfWb~jResSlGg-LnuQcPPmQctxWX4El6WVQ6TtF8~fibaftgfVzrHfwluWzgTorA9Wor2aOKyr9SIVY9pcAACdLNx~bfSvvtwn-2Awt~ZOL~L3nvS6qdpH1MbhCUGG3HV7h118dVFMQ5sIxKZi5dpE7ctRYLYTZa6TenHpHAoGhorbG7jqwKyULP7DGFRUR~IJbN3B8r3IcDlofw__\",\"signed_captions\":[{\"language\":\"en\",\"url\":\"https://substackcdn.com/video_upload/post/190777516/f7a9aba8-7fe1-4ab1-a5c6-c6a9d16344dc/1773352418/en.vtt?Expires=1775560045&Key-Pair-Id=APKAIVDA3NPSMPSPESQQ&Signature=CD0zxTaLiSBs84CmkvQRZUr2PO9sEO5jDN~rPtLpRH6Y~SLdqikCyuOOADJ2oCaED8BFy~kZap8xKcZ1Rcsa343wtxkYzDp2fY3WHRPq8Jox-6oenyMkGlf1EhzkiftL8Ztb5A7pigt-HuRKfxsKtGkXUCLrxSfXTvJC-M0bdCk7zrEN7MfNr4haVXo0qb1quGF6q29ZCiB2e-HQgSpm-Gd8WNlu1ABNlNQX9h3pcTh5nMq-Lez2WwSXunX7kH0Leu0EK7TrNzjtw1bUjc9FmsA8~258oHlDeF9YHuLI-J1vCEpEiqCjYZFMNmBmrn1evWPFpEzH9OBS4XbKjshLWQ__\",\"original\":true}]}},\"podcastPreviewUpload\":null,\"voiceover_upload_id\":null,\"voiceoverUpload\":null,\"has_voiceover\":false,\"description\":\"Turbopuffer came out of a reading app.\",\"body_html\":\"
Turbopuffer came out of a reading app.

In 2022, Simon was helping his friends at Readwise scale their infra for a highly requested feature: article recommendations and semantic search. Readwise was paying ~$5k/month for their relational database and vector search would cost ~$20k/month making the feature too expensive to ship. In 2023 after mulling over the problem from Readwise, Simon decided he wanted to \u201Cbuild a search engine\u201D which became Turbopuffer.

Turbopuffer helping Readwise today - https://turbopuffer.com/customers/readwise

We discuss:
\u2022 Simon\u2019s path: Denmark \u2192 Shopify infra for nearly a decade \u2192 \u201Cangel engineering\u201D across startups like Readwise, Replicate, and Causal \u2192 turbopuffer almost accidentally becoming a company 
\u2022 The Readwise origin story: building an early recommendation engine right after the ChatGPT moment, seeing it work, then realizing it would cost ~$30k/month for a company spending ~$5k/month total on infra and getting obsessed with fixing that cost structure 
\u2022 Why turbopuffer is \u201Ca search engine for unstructured data\u201D: Simon\u2019s belief that models can learn to reason, but can\u2019t compress the world\u2019s knowledge into a few terabytes of weights, so they need to connect to systems that hold truth in full fidelity 
\u2022 The three ingredients for building a great database company: a new workload, a new storage architecture, and the ability to eventually support every query plan customers will want on their data 
\u2022 The architecture bet behind turbopuffer: going all in on object storage and NVMe, avoiding a traditional consensus layer, and building around the cloud primitives that only became possible in the last few years 

\u2022 Why Simon hated operating Elasticsearch at Shopify: years of painful on-call experience shaped his obsession with simplicity, performance, and eliminating state spread across multiple systems 
\u2022 The Cursor story: launching turbopuffer as a scrappy side project, getting an email from Cursor the next day, flying out after a 4am call, and helping cut Cursor\u2019s costs by 95% while fixing their per-user economics 

\u2022 The Notion story: buying dark fiber, tuning TCP windows, and eating cross-cloud costs because Simon refused to compromise on architecture just to close a deal faster 

\u2022 Why AI changes the build-vs-buy equation: it\u2019s less about whether a company can build search infra internally, and more about whether they have time especially if an external team can feel like an extension of their own 
\u2022 Why RAG isn\u2019t dead: coding companies still rely heavily on search, and Simon sees hybrid retrieval semantic, text, regex, SQL-style patterns becoming more important, not less 
\u2022 How agentic workloads are changing search: the old pattern was one retrieval call up front; the new pattern is one agent firing many parallel queries at once, turning search into a highly concurrent tool call 
\u2022 Why turbopuffer is reducing query pricing: agentic systems are dramatically increasing query volume, and Simon expects retrieval infra to adapt to huge bursts of concurrent search rather than a small number of carefully chosen calls 
\u2022 The philosophy of \u201Cplaying with open cards\u201D: Simon\u2019s habit of being radically honest with investors, including telling Lachy Groom he\u2019d return the money if turbopuffer didn\u2019t hit PMF by year-end 
\u2022 The \u201CP99 engineer\u201D: Simon\u2019s framework for building a talent-dense company, rejecting by default unless someone on the team feels strongly enough to fight for the candidate 

\u2014

Simon H\u00F8rup Eskildsen
\u2022 LinkedIn: https://www.linkedin.com/in/sirupsen
\u2022 X: https://x.com/Sirupsen
\u2022 https://sirupsen.com/about

turbopuffer
\u2022 https://turbopuffer.com/

## Full Video Pod

## Timestamps

00:00:00 The PMF promise to Lachy Groom
00:00:25 Intro and Simon's background
00:02:19 What turbopuffer actually is
00:06:26 Shopify, Elasticsearch, and the pain behind the company
00:10:07 The Readwise experiment that sparked turbopuffer
00:12:00 The insight Simon couldn\u2019t stop thinking about
00:17:00 S3 consistency, NVMe, and the architecture bet
00:20:12 The Notion story: latency, dark fiber, and conviction
00:25:03 Build vs. buy in the age of AI
00:26:00 The Cursor story: early launch to breakout customer
00:29:00 Why code search still matters
00:32:00 Search in the age of agents
00:34:22 Pricing turbopuffer in the AI era
00:38:17 Why Simon chose Lachy Groom
00:41:28 Becoming a founder on purpose
00:44:00 The \u201CP99 engineer\u201D philosophy
00:49:30 Bending software to your will
00:51:13 The future of turbopuffer
00:57:05 Simon\u2019s tea obsession
00:59:03 Tea kits, X Live, and P99 Live

## Transcript

Simon H\u00F8rup Eskildsen: I don\u2019t think I\u2019ve said this publicly before, but I just called Lockey and was like, local Lockie. Like if this doesn\u2019t have PMF by the end of the year, like we\u2019ll just like return all the money to you. But it\u2019s just like, I don\u2019t really, we, Justine and I don\u2019t wanna work on this unless it\u2019s really working.

So we want to give it the best shot this year and like we\u2019re really gonna go for it. We\u2019re gonna hire a bunch of people. We\u2019re just gonna be honest with everyone. Like when I don\u2019t know how to play a game, I just play with open cards. Lockey was the only person that didn\u2019t, that didn\u2019t freak out. He was like, I\u2019ve never heard anyone say that before.

Alessio: Hey everyone, welcome to the Leading Space podcast. This is Celesio Pando, Colonel Laz, and I\u2019m joined by Swix, editor of Leading Space.

swyx: Hello. Hello, uh, we\u2019re still, uh, recording in the Ker studio for the first time. Very excited. And today we are joined by Simon Eski. Of Turbo Farer welcome.

Simon H\u00F8rup Eskildsen: Thank you so much for having me.

swyx: Turbo Farer has like really gone on a huge tear, and I, I do have to mention that like you\u2019re one of, you\u2019re not my newest member of the Danish AHU Mafia, where like there\u2019s a lot of legendary programmers that have come out of it, like, uh, beyond Trotro, Rasmus, lado Berg and the V eight team and, and Google Maps team.

Uh, you\u2019re mostly a Canadian now, but isn\u2019t that interesting? There\u2019s so many, so much like strong Danish presence.

Simon H\u00F8rup Eskildsen: Yeah, I was writing a post, um, not that long ago about sort of the influences. So I grew up in Denmark, right? I left, I left when, when I was 18 to go to Canada to, to work at Shopify. Um, and so I, like, I\u2019ve, I would still say that I feel more Danish than, than Canadian.

This is also the weird accent. I can\u2019t say th because it, this is like, I don\u2019t, you know, my wife is also Canadian, um, and I think. I think like one of the things in, in Denmark is just like, there\u2019s just such a ruthless pragmatism and there\u2019s also a big focus on just aesthetics. Like, they\u2019re like very, people really care about like where, what things look like.

Um, and like Canada has a lot of attributes, US has, has a lot of attributes, but I think there\u2019s been lots of the great things to carry. I don\u2019t know what\u2019s in the water in Ahu though. Um, and I don\u2019t know that I could be considered part of the Mafi mafia quite yet, uh, compared to the phenomenal individuals we just mentioned.

Barra OV is also, uh, Danish Canadian. Okay. Yeah. I don\u2019t know where he lives now, but, and he\u2019s the PHP.

swyx: Yeah. And obviously Toby German, but moved to Canada as well. Yes. Like this is like import that, uh, that, that is an interesting, um, talent move.

Alessio: I think. I would love to get from you. Definition of Turbo puffer, because I think you could be a Vector db, which is maybe a bad word now in some circles, you could be a search engine.

It\u2019s like, let, let\u2019s just start there and then we\u2019ll maybe run through the history of how you got to this point.

Simon H\u00F8rup Eskildsen: For sure. Yeah. So Turbo Puffer is at this point in time, a search engine, right? We do full text search and we do vector search, and that\u2019s really what we\u2019re specialized in. If you\u2019re trying to do much more than that, like then this might not be the right place yet, but Turbo Buffer is all about search.

The other way that I think about it is that we can take all of the world\u2019s knowledge, all of the exabytes and exabytes of data that there is, and we can use those tokens to train a model, but we can\u2019t compress all of that into a few terabytes of weights, right? Compress into a few terabytes of weights, how to reason with the world, how to make sense of the knowledge.

But we have to somehow connect it to something externally that actually holds that like in full fidelity and truth. Um, and that\u2019s the thing that we intend to become. Right? That\u2019s like a very holier than now kind of phrasing, right? But being the search engine for unstructured, unstructured data is the focus of turbo puffer at this point in time.

Alessio: And let\u2019s break down. So people might say, well, didn\u2019t Elasticsearch already do this? And then some other people might say, is this search on my data, is this like closer to rag than to like a xr, like a public search thing? Like how, how do you segment like the different types of search?

Simon H\u00F8rup Eskildsen: The way that I generally think about this is like, there\u2019s a lot of database companies and I think if you wanna build a really big database company, sort of, you need a couple of ingredients to be in the air.

We don\u2019t, which only happens roughly every 15 years. You need a new workload. You basically need the ambition that every single company on earth is gonna have data in your database. Multiple times you look at a company like Oracle, right? You will, like, I don\u2019t think you can find a company on earth with a digital presence that it not, doesn\u2019t somehow have some data in an Oracle database.

Right? And I think at this point, that\u2019s also true for Snowflake and Databricks, right? 15 years later it\u2019s, or even more than that, there\u2019s not a company on earth that doesn\u2019t, in. Or directly is consuming Snowflake or, or Databricks or any of the big analytics databases. Um, and I think we\u2019re in that kind of moment now, right?

I don\u2019t think you\u2019re gonna find a company over the next few years that doesn\u2019t directly or indirectly, um, have all their data available for, for search and connect it to ai. So you need that new workload, like you need something to be happening where there\u2019s a new workload that causes that to happen, and that new workload is connecting very large amounts of data to ai.

The second thing you need. The second condition to build a big database company is that you need some new underlying change in the storage architecture that is not possible from the databases that have come before you. If you look at Snowflake and Databricks, right, commoditized, like massive fleet of HDDs, like that was not possible in it.

It just wasn\u2019t in the air in the nineties, right? So you just didn\u2019t, we just didn\u2019t build these systems. S3 and and and so on was not around. And I think the architecture that is now possible that wasn\u2019t possible 15 years ago is to go all in on NVME SSDs. It requires a particular type of architecture for the database that.

It\u2019s difficult to retrofit onto the databases that are already there, including the ones you just mentioned. The second thing is to go all in on OIC storage, more so than we could have done 15 years ago. Like we don\u2019t have a consensus layer, we don\u2019t really have anything. In fact, you could turn off all the servers that Turbo Buffer has, and we would not lose any data because we have all completely all in on OIC storage.

And this means that our architecture is just so simple. So that\u2019s the second condition, right? First being a new workload. That means that every company on earth, either indirectly or directly, is using your database. Second being, there\u2019s some new storage architecture. That means that the, the companies that have come before you can do what you\u2019re doing.

I think the third thing you need to do to build a big database company is that over time you have to implement more or less every Cory plan on the data. What that means is that you. You can\u2019t just get stuck in, like, this is the one thing that a database does. It has to be ever evolving because when someone has data in the database, they over time expect to be able to ask it more or less every question.

So you have to do that to get the storage architecture to the limit of what, what it\u2019s capable of. Those are the three conditions.

swyx: I just wanted to get a little bit of like the motivation, right? Like, so you left Shopify, you\u2019re like principal, engineer, infra guy. Um, you also head of kernel labs, uh, inside of Shopify, right?

And then you consulted for read wise and that it kind of gave you that, that idea. I just wanted you to tell that story. Um, maybe I, you\u2019ve told it before, but, uh, just introduce the, the. People to like the, the new workload, the sort of aha moment for turbo Puffer

Simon H\u00F8rup Eskildsen: For sure. So yeah, I spent almost a decade at Shopify.

I was on the infrastructure team, um, from the fairly, fairly early days around 2013. Um, at the time it felt like it was growing so quickly and everything, all the metrics were, you know, doubling year on year compared to the, what companies are contending with today. It\u2019s very cute in growth. I feel like lot some companies are seeing that month over month.

Um, of course. Shopify compound has been compounding for a very long time now, but I spent a decade doing that and the majority of that was just make sure the site is up today and make sure it\u2019s up a year from now. And a lot of that was really just the, um, you know, uh, the Kardashians would drive very, very large amounts of, of data to, to uh, to Shopify as they were rotating through all the merch and building out their businesses.

And we just needed to make sure we could handle that. Right. And sometimes these were events, a million requests per second. And so, you know, we, we had our own data centers back in the day and we were moving to the cloud and there was so much sharding work and all of that that we were doing. So I spent a decade just scaling databases \u2018cause that\u2019s fundamentally what\u2019s the most difficult thing to scale about these sites.

The database that was the most difficult for me to scale during that time, and that was the most aggravating to be on call for, was elastic search. It was very, very difficult to deal with. And I saw a lot of projects that were just being held back in their ambition by using it.

swyx: And I mean, self-hosted.

Self-hosted. \u2018cause

Simon H\u00F8rup Eskildsen: it\u2019s, yeah, and it commercial, this is like 2015, right? So it\u2019s like a very particular vintage. Right. It\u2019s probably better at a lot of these things now. Um, it was difficult to contend with and I\u2019m just like, I just think about it. It\u2019s an inverted index. It should be good at these kinds of queries and do all of this.

And it was, we, we often couldn\u2019t get it to do exactly what we needed to do or basically get lucine to do, like expose lucine raw to, to, to what we needed to do. Um, so that was like. Just something that we did on the side and just panic scaled when we needed to, but not a particular focus of mine. So I left, and when I left, I, um, wasn\u2019t sure exactly what I wanted to do.

I mean, it spent like a decade inside of the same company. I\u2019d like grown up there. I started working there when I was 18.

swyx: You only do Rails?

Simon H\u00F8rup Eskildsen: Yeah. I mean, yeah. Rails. And he\u2019s a Rails guy. Uh, love Rails. So good. Um,

Alessio: we all wish we could still work in Rails.

swyx: I know know. I know, but some, I tried learning Ruby.

It\u2019s just too much, like too many options to do the same thing. It\u2019s, that\u2019s my, I I know there\u2019s a, there\u2019s a way to do it.

Simon H\u00F8rup Eskildsen: I love it. I don\u2019t know that I would use it now, like given cloud code and, and, and cursor and everything, but, um, um, but still it, like if I\u2019m just sitting down and writing a teal code, that\u2019s how I think.

But anyway, I left and I wasn\u2019t, I talked to a couple companies and I was like, I don\u2019t. I need to see a little bit more of the world here to know what I\u2019m gonna like focus on next. Um, and so what I decided is like I was gonna, I called it like angel engineering, where I just hopped around in my friend\u2019s companies in three months increments and just helped them out with something.

Right. And, and just vested a bit of equity and solved some interesting infrastructure problem. So I worked with a bunch of companies at the time, um, read Wise was one of them. Replicate was one of them. Um, causal, I dunno if you\u2019ve tried this, it\u2019s like a, it\u2019s a spreadsheet engine Yeah. Where you can do distribution.

They sold recently. Yeah. Um, we\u2019ve been, we used that in fp and a at, um, at Turbo Puffer. Um, so a bunch of companies like this and it was super fun. And so we\u2019re the Chachi bt moment happened, I was with. With read Wise for a stint, we were preparing for the reader launch, right? Which is where you, you cue articles and read them later.

And I was just getting their Postgres up to snuff, like, which basically boils down to tuning, auto vacuum. So I was doing that and then this happened and we were like, oh, maybe we should build a little recommendation engine and some features to try to hook in the lms. They were not that good yet, but it was clear there was something there.

And so I built a small recommendation engine just, okay, let\u2019s take the articles that you\u2019ve recently read, right? Like embed all the articles and then do recommendations. It was good enough that when I ran it on one of the co-founders of Rey\u2019s, like I found out that I got articles about, about having a child.

I\u2019m like, oh my God, I didn\u2019t, I, I didn\u2019t know that, that they were having a child. I wasn\u2019t sure what to do with that information, but the recommendation engine was good enough that it was suggesting articles, um, about that. And so there was, there was recommendations and uh, it actually worked really well.

But this was a company that was spending maybe five grand a month in total on all their infrastructure and. When I did the napkin math on running the embeddings of all the articles, putting them into a vector index, putting it in prod, it\u2019s gonna be like 30 grand a month. That just wasn\u2019t tenable. Right?

Like Read Wise is a proudly bootstrapped company and it\u2019s paying 30 grand for infrastructure for one feature versus five. It just wasn\u2019t tenable. So sort of in the bucket of this is useful, it\u2019s pretty good, but let us, let\u2019s return to it when the costs come down.

swyx: Did you say it grows by feature? So for five to 30 is by the number of, like, what\u2019s the, what\u2019s the Scaling factor scale?

It scales by the number of articles that you embed.

Simon H\u00F8rup Eskildsen: It does, but what I meant by that is like five grand for like all of the other, like the Heroku, dinos, Postgres, like all the other, and this then storage is 30. Yeah. And then like 30 grand for one feature. Right. Which is like, what other articles are related to this one.

Um, so it was just too much right to, to power everything. Their budget would\u2019ve been maybe a few thousand dollars, which still would\u2019ve been a lot. And so we put it in a bucket of, okay, we\u2019re gonna do that later. We\u2019ll wait, we will wait for the cost to come down. And that haunted me. I couldn\u2019t stop thinking about it.

I was like, okay, there\u2019s clearly some latent demand here. If the cost had been a 10th, we would\u2019ve shipped it and. This was really the only data point that I had. Right. I didn\u2019t, I, I didn\u2019t, I didn\u2019t go out and talk to anyone else. It was just so I started reading Right. I couldn\u2019t, I couldn\u2019t help myself.

Like I didn\u2019t know what like a vector index is. I, I generally barely do about how to generate the vectors. There was a lot of hype about, this is a early 2023. There was a lot of hype about vector databases. There were raising a lot of money and it\u2019s like, I really didn\u2019t know anything about it. It\u2019s like, you know, trying these little models, fine tuning them.

Like I was just trying to get sort of a lay of the land. So I just sat down. I have this. A GitHub repository called Napkin Math. And on napkin math, there\u2019s just, um, rows of like, oh, this is how much bandwidth. Like this is how many, you know, you can do 25 gigabytes per second on average to dram. You can do, you know, five gigabytes per second of rights to an SSD, blah blah.

All of these numbers, right? And S3, how many you could do per, how much bandwidth can you drive per connection? I was just sitting down, I was like, why hasn\u2019t anyone build a database where you just put everything on O storage and then you puff it into NVME when you use the data and you puff it into dram if you\u2019re, if you\u2019re querying it alive, it\u2019s just like, this seems fairly obvious and you, the only real downside to that is that if you go all in on o storage, every right will take a couple hundred milliseconds of latency, but from there it\u2019s really all upside, right?

You do the first go, it takes half a second. And it sort of occurred to me as like, well. The architecture is really good for that. It\u2019s really good for AB storage, it\u2019s really good for nvm ESSD. It\u2019s, well, you just couldn\u2019t have done that 10 years ago. Back to what we were talking about before. You really have to build a database where you have as few round trips as possible, right?

This is how CPUs work today. It\u2019s how NVM E SSDs work. It\u2019s how as, um, as three works that you want to have a very large amount of outstanding requests, right? Like basically go to S3, do like that thousand requests to ask for data in one round trip. Wait for that. Get that, like, make a new decision. Do it again, and try to do that maybe a maximum of three times.

But no databases were designed that way within NVME as is ds. You can drive like within, you know, within a very low multiple of DRAM bandwidth if you use it that way. And same with S3, right? You can fully max out the network card, which generally is not maxed out. You get very, like, very, very good bandwidth.

And, but no one had built a database like that. So I was like, okay, well can\u2019t you just, you know, take all the vectors right? And plot them in the proverbial coordinate system. Get the clusters, put a file on S3 called clusters, do json, and then put another file for every cluster, you know, cluster one, do js O cluster two, do js ON you know that like it\u2019s two round trips, right?

So you get the clusters, you find the closest clusters, and then you download the cluster files like the, the closest end. And you could do this in two round trips.

swyx: You were nearest neighbors locally.

Simon H\u00F8rup Eskildsen: Yes. Yes. And then, and you would build this, this file, right? It\u2019s just like ultra simplistic, but it\u2019s not a far shot from what the first version of Turbo Buffer was.

Why hasn\u2019t anyone done that

Alessio: in that moment? From a workload perspective, you\u2019re thinking this is gonna be like a read heavy thing because they\u2019re doing recommend. Like is the fact that like writes are so expensive now? Oh, with ai you\u2019re actually not writing that much.

Simon H\u00F8rup Eskildsen: At that point I hadn\u2019t really thought too much about, well no actually it was always clear to me that there was gonna be a lot of rights because at Shopify, the search clusters were doing, you know, I don\u2019t know, tens or hundreds of crew QPS, right?

\u2018cause you just have to have a human sit and type in. But we did, you know, I don\u2019t know how many updates there were per second. I\u2019m sure it was in the millions, right into the cluster. So I always knew there was like a 10 to 100 ratio on the read write. In the read wise use case. It\u2019s, um, even, even in the read wise use case, there\u2019d probably be a lot fewer reads than writes, right?

There\u2019s just a lot of churn on the amount of stuff that was going through versus the amount of queries. Um, I wasn\u2019t thinking too much about that. I was mostly just thinking about what\u2019s the fundamentally cheapest way to build a database in the cloud today using the primitives that you have available.

And this is it, right? You just, now you have one machine and you know, let\u2019s say you have a terabyte of data in S3, you paid the $200 a month for that, and then maybe five to 10% of that data and needs to be an NV ME SSDs and less than that in dram. Well. You\u2019re paying very, very little to inflate the data.

swyx: By the way, when you say no one else has done that, uh, would you consider Neon, uh, to be on a similar path in terms of being sort of S3 first and, uh, separating the compute and storage?

Simon H\u00F8rup Eskildsen: Yeah, I think what I meant with that is, uh, just build a completely new database. I don\u2019t know if we were the first, like it was very much, it was, I mean, I, I hadn\u2019t, I just looked at the napkin math and was like, this seems really obvious.

So I\u2019m sure like a hundred people came up with it at the same time. Like the light bulb and every invention ever. Right. It was just in the air. I think Neon Neon was, was first to it. And they\u2019re trying, they\u2019re retrofitted onto Postgres, right? And then they built this whole architecture where you have, you have it in memory and then you sort of.

You know, m map back to S3. And I think that was very novel at the time to do it for, for all LTP, but I hadn\u2019t seen a database that was truly all in, right. Not retrofitting it. The database felt built purely for this no consensus layer. Even using compare and swap on optic storage to do consensus. I hadn\u2019t seen anyone go that all in.

And I, I mean, there, there, I\u2019m sure there was someone that did that before us. I don\u2019t know. I was just looking at the napkin math

swyx: and, and when you say consensus layer, uh, are you strongly relying on S3 Strong consistency? You are. Okay.

So

Simon H\u00F8rup Eskildsen: that is your consensus layer. It, it is the consistency layer. And I think also, like, this is something that most people don\u2019t realize, but S3 only became consistent in December of 2020.

swyx: I remember this coming out during COVID and like people were like, oh, like, it was like, uh, it was just like a free upgrade.

Simon H\u00F8rup Eskildsen: Yeah.

swyx: They were just, they just announced it. We saw consistency guys and like, okay, cool.

Simon H\u00F8rup Eskildsen: And I\u2019m sure that they just, they probably had it in prod for a while and they\u2019re just like, it\u2019s done right.

And people were like, okay, cool. But. That\u2019s a big moment, right? Like nv, ME SSDs, were also not in the cloud until around 2017, right? So you just sort of had like 2017 nv, ME SSDs, and people were like, okay, cool. There\u2019s like one skew that does this, whatever, right? Takes a few years. And then the second thing is like S3 becomes consistent in 2020.

So now it means you don\u2019t have to have this like big foundation DB or like zookeeper or whatever sitting there contending with the keys, which is how. You know, that\u2019s what Snowflake and others have do so much

swyx: for gone

Simon H\u00F8rup Eskildsen: Exactly. Just gone. Right? And so just push to the, you know, whatever, how many hundreds of people they have working on S3 solved and then compare and swap was not in S3 at this point in time,

swyx: by the way.

Uh, I don\u2019t know what that is, so maybe you wanna explain. Yes. Yeah.

Simon H\u00F8rup Eskildsen: Yes. So, um, what Compare and swap is, is basically, you can imagine that if you have a database, it might be really nice to have a file called metadata json. And metadata JSON could say things like, Hey, these keys are here and this file means that, and there\u2019s lots of metadata that you have to operate in the database, right?

But that\u2019s the simplest way to do it. So now you have might, you might have a lot of servers that wanna change the metadata. They might have written a file and want the metadata to contain that file. But you have a hundred nodes that are trying to contend with this metadata that JSON well, what compare and Swap allows you to do is basically just you download the file, you make the modifications, and then you write it only if it hasn\u2019t changed.

While you did the modification and if not you retry. Right? Should just have this retry loops. Now you can imagine if you have a hundred nodes doing that, it\u2019s gonna be really slow, but it will converge over time. That primitive was not available in S3. It wasn\u2019t available in S3 until late 2024, but it was available in GCP.

The real story of this is certainly not that I sat down and like bake brained it. I was like, okay, we\u2019re gonna start on GCS S3 is gonna get it later. Like it was really not that we started, we got really lucky, like we started on GCP and we started on GCP because tur um, Shopify ran on GCP. And so that was the platform I was most available with.

Right. Um, and I knew the Canadian team there \u2018cause I\u2019d worked with them at Shopify and so it was natural for us to start there. And so when we started building the database, we\u2019re like, oh yeah, we have to build a, we really thought we had to build a consensus layer, like have a zookeeper or something to do this.

But then we discovered the compare and swap. It\u2019s like, oh, we can kick the can. Like we\u2019ll just do metadata r json and just, it\u2019s fine. It\u2019s probably fine. Um, and we just kept kicking the can until we had very, very strong conviction in the idea. Um, and then we kind of just hinged the company on the fact that S3 probably was gonna get this, it started getting really painful in like mid 2024.

\u2018cause we were closing deals with, um, um, notion actually that was running in AWS and we\u2019re like, trust us. You, you really want us to run this in GCP? And they\u2019re like, no, I don\u2019t know about that. Like, we\u2019re running everything in AWS and the latency across the cloud were so big and we had so much conviction that we bought like, you know, dark fiber between the AWS regions in, in Oregon, like in the InterExchange and GCP is like, we\u2019ve never seen a startup like do like, what\u2019s going on here?

And we\u2019re just like, no, we don\u2019t wanna do this. We were tuning like TCP windows, like everything to get the latency down \u2018cause we had so high conviction in not doing like a, a metadata layer on S3. So those were the three conditions, right? Compare and swap. To do metadata, which wasn\u2019t in S3 until late 2024 S3 being consistent, which didn\u2019t happen until December, 2020.

Uh, 2020. And then NVMe ssd, which didn\u2019t end in the cloud until 2017.

swyx: I mean, in some ways, like a very big like cloud success story that like you were able to like, uh, put this all together, but also doing things like doing, uh, bind our favor. That that actually is something I\u2019ve never heard.

Simon H\u00F8rup Eskildsen: I mean, it\u2019s very common when you\u2019re a big company, right?

You\u2019re like connecting your own like data center or whatever. But it\u2019s like, it was uniquely just a pain with notion because the, um, the org, like most of the, like if you\u2019re buying in Ashburn, Virginia, right? Like US East, the Google, like the GCP and, and AWS data centers are like within a millisecond on, on each other, on the public exchanges.

But in Oregon uniquely, the GCP data center sits like a couple hundred kilometers, like east of Portland and the AWS region sits in Portland, but the network exchange they go through is through Seattle. So it\u2019s like a full, like 14 milliseconds or something like that. And so anyway, yeah. It\u2019s, it\u2019s, so we were like, okay, we can\u2019t, we have to go through an exchange in Portland.

Yeah. And

swyx: you\u2019d rather do this than like run your zookeeper and like

Simon H\u00F8rup Eskildsen: Yes. Way rather. It doesn\u2019t have state, I don\u2019t want state and two systems. Um, and I think all that is just informed by Justine, my co-founder and I had just been on call for so long. And the worst outages are the ones where you have state in multiple places that\u2019s not syncing up.

So it really came from, from a a, like just a, a very pure source of pain, of just imagining what we would be Okay. Being woken up at 3:00 AM about and having something in zookeeper was not one of them.

swyx: You, you\u2019re talking to like a notion or something. Do they care or do they just, they

Simon H\u00F8rup Eskildsen: just, they care about latency.

swyx: They latency cost. That\u2019s it.

Simon H\u00F8rup Eskildsen: They just cared about latency. Right. And we just absorbed the cost. We\u2019re just like, we have high conviction in this. At some point we can move them to AWS. Right. And so we just, we, we\u2019ll buy the fiber, it doesn\u2019t matter. Right. Um, and it\u2019s like $5,000. Usually when you buy fiber, you buy like multiple lines.

And we\u2019re like, we can only afford one, but we will just test it that when it goes over the public internet, it\u2019s like super smooth. And so we did a lot of, anyway, it\u2019s, yeah, it was, that\u2019s cool.

Alessio: You can imagine talking to the GCP rep and it\u2019s like, no, we\u2019re gonna buy, because we know we\u2019re gonna turn, we\u2019re gonna turn from you guys and go to AWS in like six months.

But in the meantime we\u2019ll do this. It\u2019s

Simon H\u00F8rup Eskildsen: a, I mean, like they, you know, this workload still runs on GCP for what it\u2019s worth. Right? \u2018cause it\u2019s so, it was just, it was so reliable. So it was never about moving off GCP, it was just about honesty. It was just about giving notion the latency that they deserved.

Right. Um, and we didn\u2019t want \u2018em to have to care about any of this. We also, they were like, oh, egress is gonna be bad. It was like, okay, screw it. Like we\u2019re just gonna like vvc, VPC peer with you and AWS we\u2019ll eat the cost. Yeah. Whatever needs to be done.

Alessio: And what were the actual workloads? Because I think when you think about ai, it\u2019s like 14 milliseconds.

It\u2019s like really doesn\u2019t really matter in the scheme of like a model generation.

Simon H\u00F8rup Eskildsen: Yeah. We were told the latency, right. That we had to beat. Oh, right. So, so we\u2019re just looking at the traces. Right. And then sort of like hand draw, like, you know, kind of like looking at the trace and then thinking what are the other extensions of the trace?

Right. And there\u2019s a lot more to it because it\u2019s also when you have, if you have 14 versus seven milliseconds, right. You can fit in another round trip. So we had to tune TCP to try to send as much data in every round trip, prewarm all the connections. And there was, there\u2019s a lot of things that compound from having these kinds of round trips, but in the grand scheme it was just like, well, we have to beat the latency of whatever we\u2019re up against.

swyx: Which is like they, I mean, notion is a database company. They could have done this themselves. They, they do lots of database engineering themselves. How do you even get in the door? Like Yeah, just like talk through that kind of.

Simon H\u00F8rup Eskildsen: Last time I was in San Francisco, I was talking to one of the engineers actually, who, who was one of our champions, um, at, AT Notion.

And they were, they were just trying to make sure that the, you know, per user cost matched the economics that they needed. You know, Uhhuh like, it\u2019s like the way I think about, it\u2019s like I have to earn a return on whatever the clouds charge me and then my customers have to earn a return on that. And it\u2019s like very simple, right?

And so there has to be gross margin all the way up and that\u2019s how you build the product. And so then our customers have to make the right set of trade off the turbo Puffer makes, and if they\u2019re happy with that, that\u2019s great.

swyx: Do you feel like you\u2019re competing with build internally versus buy or buy versus buy?

Simon H\u00F8rup Eskildsen: Yeah, so, sorry, this was all to build up to your question. So one of the notion engineers told me that they\u2019d sat and probably on a napkin, like drawn out like, why hasn\u2019t anyone built this? And then they saw terrible. It was like, well, it literally that. So, and I think AI has also changed the buy versus build equation in terms of, it\u2019s not really about can we build it, it\u2019s about do we have time to build it?

I think they like, I think they felt like, okay, if this is a team that can do that and they, they feel enough like an extension of our team, well then we can go a lot faster, which would be very, very good for them. And I mean, they put us through the, through the test, right? Like we had some very, very long nights to to, to do that POC.

And they were really our biggest, our second big customer off the cursor, which also was a lot of late nights. Right.

swyx: Yeah. That, I mean, should we go into that story? The, the, the sort of Chris\u2019s story, like a lot, um, they credit you a lot for. Working very closely with them. So I just wanna hear, I\u2019ve heard this, uh, story from Sole\u2019s point of view, but like, I\u2019m curious what, what it looks like from your side.

Simon H\u00F8rup Eskildsen: I actually haven\u2019t heard it from Sole\u2019s point of view, so maybe you can now cross reference it. The way that I remember it was that, um, the day after we launched, which was just, you know, I\u2019d worked the whole summer on, on the first version. Justine wasn\u2019t part of it yet. \u2018cause I just, I didn\u2019t tell anyone that summer that I was working on this.

I was just locked in on building it because it\u2019s very easy otherwise to confuse talking about something to actually doing it. And so I was just like, I\u2019m not gonna do that. I\u2019m just gonna do the thing. I launched it and at this point turbo puffer is like a rust binary running on a single eight core machine in a T Marks instance.

And me deploying it was like looking at the request log and then like command seeing it or like control seeing it to just like, okay, there\u2019s no request. Let\u2019s upgrade the binary. Like it was like literally the, the, the, the scrappiest thing. You could imagine it was on purpose because just like at Shopify, we did that all the time.

Like, we like move, like we ran things in tux all the time to begin with. Before something had like, at least the inkling of PMF, it was like, okay, is anyone gonna hear about this? Um, and one of the cursor co-founders Arvid reached out and he just, you know, the, the cursor team are like all I-O-I-I-M-O like, um, contenders, right?

So they just speak in bullet points and, and facts. It was like this amazing email exchange just of, this is how many QPS we have, this is what we\u2019re paying, this is where we\u2019re going, blah, blah, blah. And so we\u2019re just conversing in bullet points. And I tried to get a call with them a few times, but they were, so, they were like really writing the PMF bowl here, just like late 2023.

And one time Swally emails me at like five. What was it like 4:00 AM Pacific time saying like, Hey, are you open for a call now? And I\u2019m on the East coast and I, it was like 7:00 AM I was like, yeah, great, sure, whatever. Um, and we just started talking and something. Then I didn\u2019t know anything about sales.

It was something that just comp compelled me. I have to go see this team. Like, there\u2019s something here. So I, I went to San Francisco and I went to their office and the way that I remember it is that Postgres was down when I showed up at the office. Did SW tell you this? No. Okay. So Postgres was down and so it\u2019s like they were distracting with that.

And I was trying my best to see if I could, if I could help in any way. Like I knew a little bit about databases back to tuning, auto vacuum. It was like, I think you have to tune out a vacuum. Um, and so we, we talked about that and then, um, that evening just talked about like what would it look like, what would it look like to work with us?

And I just said. Look like we\u2019re all in, like we will just do what we\u2019ll do whatever, whatever you tell us, right? They migrated everything over the next like week or two, and we reduced their cost by 95%, which I think like kind of fixed their per user economics. Um, and it solved a lot of other things. And we were just, Justine, this is also when I asked Justine to come on as my co-founder, she was the best engineer, um, that I ever worked with at Shopify.

She lived two blocks away and we were just, okay, we\u2019re just gonna get this done. Um, and we did, and so we helped them migrate and we just worked like hell over the next like month or two to make sure that we were never an issue. And that was, that was the cursor story. Yeah.

swyx: And, and is code a different workload than normal text?

I, I don\u2019t know. Is is it just text? Is it the same thing?

Simon H\u00F8rup Eskildsen: Yeah, so cursor\u2019s workload is basically, they, um, they will embed the entire code base, right? So they, they will like chunk it up in whatever they would, they do. They have their own embedding model, um, which they\u2019ve been public about. Um, and they find that on, on, on their evals.

It. There\u2019s one of their evals where it\u2019s like a 25% improvement on a very particular workload. They have a bunch of blog posts about it. Um, I think it works best on larger code basis, but they\u2019ve trained their own embedding model to do this. Um, and so you\u2019ll see it if you use the cursor agent, it will do searches.

And they\u2019ve also been public around, um, how they\u2019ve, I think they post trained their model to be very good at semantic search as well. Um, and that\u2019s, that\u2019s how they use it. And so it\u2019s very good at, like, can you find me on the code that\u2019s similar to this, or code that does this? And just in, in this queries, they also use GR to supplement it.

swyx: Yeah.

Simon H\u00F8rup Eskildsen: Um, of course

swyx: it\u2019s been a big topic of discussion like, is rag dead because gr you know,

Simon H\u00F8rup Eskildsen: and I mean like, I just, we, we see lots of demand from the coding company to ethics

swyx: search in every part. Yes.

Simon H\u00F8rup Eskildsen: Uh, we, we, we see demand. And so, I mean, I\u2019m. I like case studies. I don\u2019t like, like just doing like thought pieces on this is where it\u2019s going.

And like trying to be all macroeconomic about ai, that\u2019s has turned out to be a giant waste of time because no one can really predict any of this. So I just collect case