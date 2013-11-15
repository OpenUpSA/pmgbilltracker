import datetime
from pmg_backend.models import Bill, Agent, Location, Stage, Event, Version, Content, ContentType
from pmg_backend import db

na_reports = [
    {"date": ["8 Nov 2013"], "link": ["/report/20131108-revised-committee-report-protection-state-information-bill-minister-state-security-in-attendance"], "title": ["Revised Committee Report on Protection of State Information Bill, with Minister of State Security in attendance"]},
    {"date": ["30 Oct 2013"], "link": ["/report/20131030-protection-state-information-bill-adoption-revised-committee-report-minutes-in-presence-minister"], "title": ["Protection of State Information Bill: Adoption of revised Committee Report & Minutes - in presence of the Minister"]},
    {"date": ["29 Oct 2013"], "link": ["/report/20131029-protection-state-information-bill-adoption-minutes-in-presence-minister-state-security"], "title": ["Protection of State Information Bill: Adoption of minutes, in presence of Minister of State Security"]},
    {"date": ["10 Oct 2013"], "link": ["/report/20131010-protection-state-information-bill-referral-back-president"], "title": ["Protection of State Information Bill: referral back by President"]},
    {"date": ["9 Oct 2013"], "link": ["/report/20131009-election-chairperson-clauses-42-and-45-deliberations"], "title": ["Election of Chairperson; Clauses 42 and 45: deliberations"]},
    {"date": ["23 Apr 2013"], "link": ["/report/20130423-protection-state-information-bill-and-committee-report-adoption"], "title": ["Protection of State Information Bill and Committee Report: Adoption"]},
    {"date": ["21 Apr 2013"], "link": ["/report/20130421-protection-state-information-bill-ncop-proposals-accepted"], "title": ["Protection of State Information Bill: NCOP proposals accepted"]},
    {"date": ["14 Mar 2013"], "link": ["/report/20130314-procedural-matters-parliamentary-law-advisors-briefing-proposals-ncop"], "title": ["Procedural matters: Parliamentary Law Advisor's briefing; Proposals of NCOP: State Law Advisor's briefing"]},
    {"date": ["13 Mar 2013"], "link": ["/report/20130313-consideration-committee-programme"], "title": ["Ad Hoc Committee on the Protection of Information Bill Committee Programme"]},
    {"date": ["17 Nov 2011"], "link": ["/report/20111118-protection-state-information-bill-committee-report-formal-proposals-a"], "title": ["Protection of State Information Bill: Committee Report on formal proposals for amendments"]},
    {"date": ["16 Nov 2011"], "link": ["/report/20111117-protection-state-information-bill-amendments-proposed-ifp"], "title": ["Protection of State Information Bill: Amendments proposed by IFP"]},
    {"date": ["4 Sep 2011"], "link": ["/report/20110905-protection-state-information-bill-memorandum-objects-adoption-bill"], "title": ["Protection of State Information Bill: Memorandum on Objects, Adoption of Bill"]},
    {"date": ["1 Sep 2011"], "link": ["/report/20110902-protection-state-information-bill-working-document-27"], "title": ["Protection of State Information Bill: informal vote on Working Document 27"]},
    {"date": ["31 Aug 2011"], "link": ["/report/20110901-protection-state-information-bill-working-document-26"], "title": ["Protection of State Information Bill: Working Document 26"]},
    {"date": ["30 Aug 2011"], "link": ["/report/20110831-protection-state-information-bill-working-document-25-and-committee-p"], "title": ["Protection of State Information Bill: Working Document 25"]},
    {"date": ["29 Aug 2011"], "link": ["/report/20110830-protection-state-information-bill-working-document-24-and-committee-p"], "title": ["Protection of State Information Bill: Working Document 24 and Committee Proposals 24"]},
    {"date": ["25 Aug 2011"], "link": ["/report/20110826-protection-state-information-bill-working-document-22-and-committee-p"], "title": ["Protection of State Information Bill: Working Document 22, and Committee proposals 22"]},
    {"date": ["24 Aug 2011"], "link": ["/report/20110825-protection-state-information-bill-working-document-21-and-committee-p"], "title": ["Protection of State Information Bill: Working Document 21 and Committee proposals 21"]},
    {"date": ["23 Aug 2011"], "link": ["/report/20110824-protection-state-information-bill-working-document-20-and-committee-p"], "title": ["Protection of State Information Bill: Working Document 20 and Committee proposals 20"]},
    {"date": ["22 Aug 2011"], "link": ["/report/20110824-consideration-proposed-amendments-protection-information-bill"], "title": ["Protection of State Information Bill: Working Document 19 and Committee proposals 19"]},
    {"date": ["21 Aug 2011"], "link": ["/report/20110822-consideration-proposed-amendments-protection-information-bill"], "title": ["Protection of State Information Bill: Committee Proposals on Working Document 18"]},
    {"date": ["18 Aug 2011"], "link": ["/report/20110819-protection-state-information-bill-working-draft-17"], "title": ["Protection of State Information Bill: Working Draft 17, outstanding issues"]},
    {"date": ["17 Aug 2011"], "link": ["/report/20110818-protection-state-information-bill-working-draft-16"], "title": ["Protection of State Information Bill: Working Draft 16"]},
    {"date": ["16 Aug 2011"], "link": ["/report/20110817-protection-state-information-bill-archival-matters-working-document-1"], "title": ["Protection of State Information Bill: Archival matters, Working Document 15, new clause 33A, 38 & 47"]},
    {"date": ["14 Aug 2011"], "link": ["/report/20110815-deliberations-protection-information-bill-clause-clause"], "title": ["Protection of State Information Bill: discussion of flagged issues in Working Document 14"]},
    {"date": ["10 Aug 2011"], "link": ["/report/20110811-protection-state-information-bill-functions-classification-review-pan"], "title": ["Protection of State Information Bill: Working Document 13; functions of Classification Review Panel and Agency"]},
    {"date": ["9 Aug 2011"], "link": ["/report/20110810-deliberations-protection-information-bill-clause-clause"], "title": ["Protection of (State) Information Bill: Nelson Mandela Foundation briefing on archive management, new Working Draft 12"]},
    {"date": ["3 Aug 2011"], "link": ["/report/20110804-protection-state-information-bill-new-working-document-11-changes-cla"], "title": ["Protection of (State) Information Bill: Working Document 11: definitions; clauses 33 - 49 changes; erroneous classification effects; clause 46 suggested amendments; Public Domain defence: IFP proposals"]},
    {"date": ["1 Aug 2011"], "link": ["/report/20110802-protection-state-information-bill-deliberations-definitions-and-new-w"], "title": ["Protection of (State) Information Bill: Deliberations on Definitions and new Working Document 10"]},
    {"date": ["31 Jul 2011"], "link": ["/report/20110801-protection-information-bill-new-working-document-clauses-44-end"], "title": ["Protection of Information Bill: New Working Document, clauses 44 to end"]},
    {"date": ["28 Jul 2011"], "link": ["/report/20110829-protection-information-bill-possible-inclusion-public-interest-defenc"], "title": ["Protection of Information Bill: Possible inclusion of public interest defence, Clauses 39 to 45"]},
    {"date": ["4 Nov 2010"], "link": ["/report/20101105-deliberations-public-hearings-protection-information-bill-b6-2010-cla"], "title": ["Protection of Information Bill: IFP, DA and ACDP proposed amendments"]},
    {"date": ["3 Nov 2010"], "link": ["/report/20101104-deliberations-protection-information-bill-b6-2010-clause-clause"], "title": ["Protection of Information Bill: input on latest version and ANC proposed amendments"]},
    {"date": ["2 Nov 2010"], "link": ["/report/20101103-protection-information-bill-deliberations"], "title": ["Protection of Information Bill: deliberations"]},
    {"date": ["28 Oct 2010"], "link": ["/report/20101029-protection-information-bill-way-forward"], "title": ["Protection of Information Bill: way forward"]},
    {"date": ["21 Oct 2010"], "link": ["/report/20101022-further-briefing-minister-concerns-raised-during-public-hearings-prot"], "title": ["Minister of State Security second meeting on concerns raised during public hearings"]},
    {"date": ["16 Sep 2010"], "link": ["/report/20100917-responses-ministry-state-security-comments-made-during-public-hearing"], "title": ["Minister of State Security response to public submissions on Protection of Information Bill"]},
    {"date": ["12 Aug 2010"], "link": ["/report/20100813-meeting-minister-postponed"], "title": ["Meeting with Minister postponed + no further meetings until Parliament re-opens in October 2010"]},
    {"date": ["9 Aug 2010"], "link": ["/report/20100810-consideration-public-hearings-comments-and-adoption-minutes"], "title": ["Protection of Information Bill: Consideration of Public Submissions"]},
    {"date": ["26 Jul 2010"], "link": ["/report/20100727-reflection-submissions-hearings-protection-information-bill"], "title": ["Protection of Information Bill: Chief State Law Advisor response to public submissions"]},
    {"date": ["21 Jul 2010"], "link": ["/report/20100722-protection-information-bill-b6-2010-public-hearings-day-2"], "title": ["Protection of Information Bill [B6-2010] Public hearings day 2"]},
    {"date": ["20 Jul 2010"], "link": ["/report/20100721-protection-information-bill-b6-2010-public-hearings"], "title": ["Protection of Information Bill [B6-2010]: Public hearings"]},
    {"date": ["19 Jul 2010"], "link": ["/report/20100720-preparations-public-hearings-protection-information-bill"], "title": ["Preparations for public hearings on Protection of Information Bill"]},
    {"date": ["29 Jun 2010"], "link": ["/report/20100630-consideration-submissions-protection-information-bill-b-6-2010"], "title": ["Consideration of Submissions for Hearings on Protection of Information Bill [B 6-2010]"]},
    {"date": ["31 May 2010"], "link": ["/report/20100601-briefing-protection-information-bill-ministry-state-security-agency"], "title": ["Protection of Information Bill & State security: Ministerial & National Intelligence Agency briefings"]},
    {"date": ["27 May 2010"], "link": ["/report/20100528-protection-information-bill-b6-%E2%80%93-2010-state-security-agency-briefing"], "title": ["Protection of Information Bill: State Security Agency briefing"]},
    {"date": ["13 May 2010"], "link": ["/report/20100514-protection-information-bill-department-state-security-briefing"], "title": ["Protection of Information Bill: Department of State Security briefing"]},
    {"date": ["27 Jul 2011"], "link": ["/report/20110728-protection-information-bill-new-drafts-clauses-17-23-classification-r"], "title": ["Protection of Information Bill: New drafts of clauses 17 to 23, Classification Review panel, whistleblower protection, definition of \u201cnational security\u201d; Deliberations on clauses 26 to 38"]},
    {"date": ["26 Jul 2011"], "link": ["/report/20110727-protection-information-bill-redrafted-clauses-17-23-classification-re"], "title": ["Protection of Information Bill: Review Panel, clauses 17 to 23, whistleblower protection, review time periods"]},
    {"date": ["25 Jul 2011"], "link": ["/report/20110726-protection-information-bill-new-draft-clauses-17-23-further-deliberat"], "title": ["Protection of Information Bill: New draft of Clauses 17 to 23: further deliberations"]},
    {"date": ["24 Jul 2011"], "link": ["/report/20110725-consideration-proposed-amendments-protection-information-bill-b6-2010"], "title": ["Protection of Information Bill: Review Panel, clauses 17 and 21, & 22"]},
    {"date": ["23 Jun 2011"], "link": ["/report/20110624-protection-information-bill-anc-revised-proposals-scope-offences-oppo"], "title": ["Protection of Information Bill: ANC concessions on scope & offences, opposition's proposals for clause 22"]},
    {"date": ["9 Jun 2011"], "link": ["/report/20110610-ad-hoc-protect-consideration-amendments-bill-consideration-report"], "title": ["Protection of Information Bill: New clause deliberations"]},
    {"date": ["2 Jun 2011"], "link": ["/report/20110603-deliberations-consideration-proposed-amendments-bill"], "title": ["Protection of Information Bill: deliberations on Clause 21 & proposed new clause; extension of life of committee"]},
    {"date": ["31 May 2011"], "link": ["/report/20110601-protection-information-bill-deliberations-clause-21"], "title": ["Protection of Information Bill: deliberations up to Clause 21"]},
    {"date": ["30 May 2011"], "link": ["/report/20110531-protection-information-bill-deliberations"], "title": ["Protection of Information Bill: deliberations on Clauses 14 to 21"]},
    {"date": ["26 May 2011"], "link": ["/report/20110527-protection-information-bill-deliberations-clauses-13-19"], "title": ["Protection of Information Bill: deliberations on Clauses 13 to 19"]},
    {"date": ["25 May 2011"], "link": ["/report/20110526-protection-information-bill-deliberations-clauses-3-13"], "title": ["Protection of Information Bill: deliberations on Clauses 3 to 13"]},
    {"date": ["23 May 2011"], "link": ["/report/20110524-protection-information-bill-deliberations-clauses-2-and-3"], "title": ["Protection of Information Bill: deliberations on Clauses 2 and 3"]},
    {"date": ["18 Apr 2011"], "link": ["/report/20110419-protection-information-bill-deliberations-clauses-1-3"], "title": ["Protection of Information Bill: deliberations on Clauses 1 to 3"]},
    {"date": ["14 Apr 2011"], "link": ["/report/20110415-protection-information-bill-b6-2010-deliberations-future-meetings"], "title": ["Protection of Information Bill: tabling political party submissions & discussing future meetings"]},
    {"date": ["31 Mar 2011"], "link": ["/report/20110401-protection-information-bill-committees-approach"], "title": ["Protection of Information Bill: Committee's approach"]},
    {"date": ["6 May 2010"], "link": ["/report/20100507-minister-state-security-briefing-protection-information-bill"], "title": ["Protection of Information Bill: Minister of State Security's briefing"]},
    {"date": ["3 May 2010"], "link": ["/report/20100504-election-chairperson"], "title": ["Election of Chairperson"]},
    {"date": ["28 Mar 2011"], "link": ["/report/20110329-protection-information-international-best-practices-ministry-state-se"], "title": ["Protection of Information: International Best Practices: Ministry of State Security briefing (Part 2)"]},
    {"date": ["21 Mar 2011"], "link": ["/report/20110322-protection-information-international-best-practices-ministry-state-se"], "title": ["Protection of Information: International Best Practices: Ministry of State Security briefing"]},
    {"date": ["14 Feb 2011"], "link": ["/report/20110215-reconstitution-ad-hoc-committee-international-practice-protection-inf"], "title": ["Reconstitution of ad hoc Committee; International practice on protection of information: Ministry of State Security presentation"]},
    {"date": ["27 Jan 2011"], "link": ["/report/20110128-protection-information-bill-b6-2010-committee-lifespan-state-law-advi"], "title": ["Protection of Information Bill: Committee lifespan & State Law Advisor's opinion on 3rd party notification under PAIA"]},
    {"date": ["26 Jan 2011"], "link": ["/report/20110127-protection-information-bill-b6-2010-state-law-advisors-opinion-notifi"], "title": ["Protection of Information Bill: State Law Advisor opinion on 3rd party notification under Promotion of Access to Information Act"]},
    {"date": ["24 Jan 2011"], "link": ["/report/20110125-protection-information-bill-b6-2010-democratic-alliance-view"], "title": ["Protection of Information Bill [B6-2010]: Democratic Alliance view"]},
    {"date": ["19 Jan 2011"], "link": ["/report/20110120-protection-information-bill-b6-2010-continuation-deliberations-day-3"], "title": ["Protection of Information Bill [B6-2010]: State Law Advisor opinion on three matters"]},
    {"date": ["18 Jan 2011"], "link": ["/report/20110119-protection-information-bill-b6-2010-two-draft-options-presented-day-2"], "title": ["Protection of Information Bill [B6-2010]: two draft options presented (day 2)"]},
    {"date": ["17 Jan 2011"], "link": ["/report/20110118-protection-information-bill-b6-2010-continuation-deliberations"], "title": ["Protection of Information Bill [B6-2010]: two draft options presented (day 1)"]},
    {"date": ["24 Nov 2010"], "link": ["/report/20101125-final-consideration-amendments-protection-information-bill-b6-2010"], "title": ["Protection of Information Bill: Proposed amendments to Clause 23 (Access to information)"]},
    {"date": ["22 Nov 2010"], "link": ["/report/20101123-protection-information-bill-consideration-amendments"], "title": ["Protection of Information Bill: Chapter 8 Proposed Amendments"]},
    {"date": ["15 Nov 2010"], "link": ["/report/20101116-protection-information-bill-b6-2010-continuation-deliberations"], "title": ["Protection of Information Bill: harmonisation with Promotion of Access to Information Act"]},
    {"date": ["11 Nov 2010"], "link": ["/report/20101112-consideration-amendments-protection-information-bill-b6-2010"], "title": ["Protection of Information Bill: hierachy of laws"]},
    {"date": ["8 Nov 2010"], "link": ["/report/20101109-protection-information-bill-b6-2010-deliberations"], "title": ["Protection of Information Bill: harmonisation with Protected Disclosures Act"]}
]

ncop_reports = [
    {"date": ["8 May 2013"], "link": ["/report/20130508-election-chairperson-committee-programme-0"], "title": ["Election of Chairperson; Committee Programme"]},
    {"date": ["27 Nov 2012"], "link": ["/report/20121127-protection-state-information-bill-adoption-committee-report-and-bill-"], "title": ["Protection of State Information Bill: Adoption of Committee Report and Bill as amended"]},
    {"date": ["21 Nov 2012"], "link": ["/report/20121121-deliberations-and-adoption-committee-proposed-amendments-protection-i"], "title": ["Protection of State Information Bill: Finalisation of deliberations"]},
    {"date": ["14 Nov 2012"], "link": ["/report/20121114-protection-state-information-bill-postponement-meeting-due-non-attend"], "title": ["Protection of State Information Bill: Postponement of meeting due to non-attendance of opposition parties"]},
    {"date": ["13 Nov 2012"], "link": ["/report/20121113-protection-state-information-bill-postponement-meeting-due-non-attend"], "title": ["Protection of State Information Bill: deliberations on Department State Security responses"]},
    {"date": ["31 Oct 2012"], "link": ["/report/20121031-state-security-agency-amendments-agreed-and-proposed-committee"], "title": ["Protection of State Information Bill: Minister of State Security response to proposed amendments"]},
    {"date": ["18 Sep 2012"], "link": ["/report/20120918-protection-state-information-act-deliberation-outstanding-issues"], "title": ["Protection of State Information Act: deliberation on outstanding issues"]},
    {"date": ["11 Sep 2012"], "link": ["/report/20120911-committee-deliberations-proposed-amendments-protection-state-informat"], "title": ["Protection of State Information Bill: further deliberations on ANC proposals"]},
    {"date": ["6 Sep 2012"], "link": ["/report/20120906-protection-state-information-bill-state-law-advisors-briefing-proposa"], "title": ["Protection of State Information Bill: State Law Advisors' briefing, proposals for clauses 1 to 14"]},
    {"date": ["29 Aug 2012"], "link": ["/report/20120829-update-department-mineral-resources"], "title": ["Protection of State Information Bill: some ANC proposals"]},
    {"date": ["7 Aug 2012"], "link": ["/report/20120807-department-state-security-responses-protection-state-information-bill"], "title": ["Department of State Security responses: Protection of State Information Bill proposed amendments"]},
    {"date": ["12 Jun 2012"], "link": ["/report/20120612-protection-state-information-bill-department-state-security-responses"], "title": ["Protection of State Information Bill: Department of State Security Responses to Committee's proposals"]},
    {"date": ["6 Jun 2012"], "link": ["/report/20120606-protection-state-information-bill-department-state-security-responses"], "title": ["Protection of State Information Bill: Department of State Security Responses to public hearings"]},
    {"date": ["10 May 2012"], "link": ["/report/20120510-protection-state-information-bill-continuation-deliberations"], "title": ["Protection of State Information Bill: party proposals"]},
    {"date": ["9 May 2012"], "link": ["/report/20120509-protection-state-information-bill-b6b-2010-continuation-deliberations"], "title": ["Protection of State Information Bill [B6B-2010]: continuation of deliberations"]},
    {"date": ["8 May 2012"], "link": ["/report/20120508-protection-state-information-bill-deliberation-public-submissions"], "title": ["Protection of State Information Bill: Deliberation on public submissions"]},
    {"date": ["4 May 2012"], "link": ["/report/20120504-protection-state-information-bill-deliberations-and-tabling-report-he"], "title": ["Protection of State Information Bill: deliberations and tabling of Report on hearings"]},
    {"date": ["30 Mar 2012"], "link": ["/report/20120330-public-hearings-protection-state-information-bill"], "title": ["Protection of State Information Bill: hearing Day 4"]},
    {"date": ["29 Mar 2012"], "link": ["/report/20120329-protection-state-information-bill-public-hearings-day-3"], "title": ["Protection of State Information Bill: public hearing Day 3"]},
    {"date": ["28 Mar 2012"], "link": ["/report/20120328-public-hearings-protection-state-information-bill"], "title": ["Protection of State Information Bill: public hearing Day 2"]},
    {"date": ["27 Mar 2012"], "link": ["/report/20120327-protection-state-information-bill-public-hearings-day-1"], "title": ["Protection of State Information Bill: public hearing Day 1"]},
    {"date": ["14 Mar 2012"], "link": ["/report/20120314-protection-state-information-bill-9b6b-2010-shortlisting-submissions"], "title": ["Protection of State Information Bill [B6B-2010]: Shortlisting of submissions"]},
    {"date": ["7 Mar 2012"], "link": ["/report/20120307-protection-state-information-bill-b6b-2010-report-back-provincial-pub"], "title": ["Protection of State Information Bill [B6B-2010]: Report back on provincial public hearings"]},
    {"date": ["24 Jan 2012"], "link": ["/report/20120124-protection-state-information-bill-b6b-2010-ministers-and-departments-"], "title": ["Protection of State Information Bill [B6B-2010]: Minister's and Department's briefing"]},
    {"date": ["17 Jan 2012"], "link": ["/report/20120117-discussion-and-adoption-ad-hoc-committee-programme"], "title": ["Protection of State Information Bill: discussion on Committee Programme"]},
    {"date": ["6 Dec 2011"], "link": ["/report/20111207-election-chairperson"], "title": ["Protection of State Information Bill NCOP Ad  Hoc Committee: Way Forward"]}
]


def new_report(report_dict, tmp_bill, tmp_stage, tmp_agent, content_type):

    tmp_date = report_dict['date'][0]
    # convert date string to datetime object
    if len(tmp_date) == 10:
        tmp_date = "0" + tmp_date
    tmp_date = datetime.datetime.strptime(tmp_date, "%d %b %Y")

    tmp_link = report_dict['link'][0]
    tmp_title = report_dict['title'][0]

    event = Event()
    event.bill = tmp_bill
    event.date = tmp_date
    event.stage = tmp_stage
    event.agent = tmp_agent

    item = Content()
    item.event = event
    item.type = content_type
    item.title = tmp_title
    item.url = "http://www.pmg.org.za" + tmp_link
    #print event
    #print item
    return event, item


def rebuild_db():
    """
    Drop and then rebuild the current database, populating it with some test data.
    """

    db.drop_all()
    db.create_all()

    b1 = Bill()
    b1.name = 'Protection of State Information Bill'
    b1.bill_type = 'Section 75 (Ordinary Bills not affecting provinces)'
    b1.objective = 'To provide for the protection of certain information from destruction, loss or unlawful disclosure; to regulate the manner in which information may be protected; to repeal the Protection of Information Act, 1982; and to provide for matters connected therewith.'
    db.session.add(b1)

    b2 = Bill()
    b2.name = 'Example Bill'
    b2.bill_type = "Section 76 (Ordinary Bills affecting the provinces)"
    b2.objective = "To demonstrate the efficacy of the PMG bill-tracking application."
    db.session.add(b2)

    b3 = Bill()
    b3.name = 'Another Example Bill'
    b3.bill_type = 'Section 75 (Ordinary Bills not affecting provinces)'
    b3.objective = "To go yet further in demonstrating the efficacy of the PMG bill-tracking application."
    db.session.add(b3)

    location_details = [
        ("National Assembly", "NA"),
        ("National Council of Provinces", "NCOP"),
        ("The Office of the President", "President's Office"),
        ]
    locations = []

    for tmp in location_details:
        location = Location()
        location.name = tmp[0]
        location.short_name = tmp[1]
        db.session.add(location)
        locations.append(location)

    agent_details = [
        ("house", "National Assembly", "NA"),
        ("house", "National Council of Provinces", "NA"),
        ("na-committee", "Ad-Hoc Committee on Protection of State Information Bill", "Ad-Hoc Committee"),
        ("ncop-committee", "Ad-Hoc Committee on Protection of State Information Bill", "Ad-Hoc Committee"),
        ("joint-committee", None, None),
        ("minister", "Minister of State Security", None),
        ("president", "The President of the Republic of South Africa", "President"),
        ("mp", None, None),
        ]

    agents = []
    for tmp in agent_details:
        agent = Agent()
        agent.type = tmp[0]
        agent.name = tmp[1]
        agent.short_name = tmp[2]
        db.session.add(agent)
        agents.append(agent)

    stage_details = [
        (locations[0], "Introduced to National Assembly", "Waiting to be assigned to a committee"),
        (locations[0], "National Assembly Committee", "Under review by National Assembly Committee"),
        (locations[0], "Public participation", "Open for public submissions"),
        (locations[0], "National Assembly", "Up for debate in the National Assembly"),
        (locations[1], "Introduced to National Council of Provinces", "Waiting to be assigned to a committee"),
        (locations[1], "National Council of Provinces Committee", "Under review by NCOP Committee"),
        (locations[1], "National Council of Provinces", "Up for debate in the NCOP"),
        (locations[0], "Mediation Committee", "Under review by Joint Committee"),
        (locations[2], "Presidential Signature", "Waiting to be signed into law"),
        ]

    stages = []
    for tmp in stage_details:
        stage = Stage()
        stage.location = tmp[0]
        stage.name = tmp[1]
        stage.default_status = tmp[2]
        db.session.add(stage)
        stages.append(stage)

    event_details = [
        (datetime.date(2010, 3, 4), stages[0], agents[5], "Introduced to parliament"),
        (datetime.date(2011, 6, 20), stages[1], agents[2], "Assigned to a committee"),
        (datetime.date(2011, 9, 4), stages[1], agents[2]),
        (datetime.date(2012, 5, 6), stages[2], agents[2]),
        (datetime.date(2013, 4, 24), stages[1], agents[2]),
        (datetime.date(2013, 5, 3), stages[1], agents[2]),
        (datetime.date(2013, 8, 20), stages[3], agents[0], "Accepted by the National Assembly"),
        (datetime.date(2013, 9, 1), stages[5], agents[3]),
        (datetime.date(2013, 9, 2), stages[6], agents[1], "Accepted by the NCOP"),
        (datetime.date(2013, 9, 3), stages[8], agents[6], "Sent back to Parliament"),
        (datetime.date(2013, 9, 4), stages[1], agents[2]),
        (datetime.date(2013, 10, 15), stages[1], agents[2]),
        ]

    events = []

    for tmp in event_details:
        event = Event()
        event.bill = b1
        event.date = tmp[0]
        event.stage = tmp[1]
        event.agent = tmp[2]
        try:
            event.new_status = tmp[3]
        except IndexError:
            event.new_status = tmp[1].default_status
        db.session.add(event)
        events.append(event)

    bill_version_details = [
        (events[0], "B6 2010", "uploads/B6-2010.pdf"),
        (events[2], "B6B 2010", "uploads/B6B-2010.pdf"),
        (events[4], "B6C 2010", "uploads/B6C-2010.pdf"),
        (events[4], "B6D 2010", "uploads/B6D-2010.pdf"),
        (events[11], "B6E 2010", "uploads/B6E-2010.pdf"),
        (events[11], "B6F 2010", "uploads/B6F-2010.pdf"),
        ]

    for tmp in bill_version_details:
        item = Version()
        item.event = tmp[0]
        item.title = tmp[1]
        item.url = tmp[2]
        db.session.add(item)

    content_type_details = [
        "gazette",
        "memorandum",
        "greenpaper",
        "whitepaper",
        "draft-bill",
        "pmg-meeting-report",
        "committee-report",
        "hansard-minutes",
        "vote-count",
        "other",
        ]

    content_types = []

    for tmp in content_type_details:
        content_type = ContentType(name=tmp)
        db.session.add(content_type)
        content_types.append(content_type)

    content_details = [
        (events[0], content_types[0], "Gazette no. 32999", "uploads/Gazette-32999_2010-03-05.pdf"),
        (events[0], content_types[3], "White Paper", "uploads/Gazette-30885_2008-03-18.pdf"),
        (events[1], content_types[5], "Meeting report: 20 June 2011", "uploads/example.pdf"),
        (events[3], content_types[5], "Meeting report: 6 May 2012 - Public Hearings", "uploads/example.pdf"),
        (events[4], content_types[6], "Committee Report", "http://www.pmg.org.za/report/20130423-protection-state-information-bill-and-committee-report-adoption"),
        (events[5], content_types[5], "Meeting report: 3 May 2013", "uploads/example.pdf"),
        (events[5], content_types[6], "Committee Report", "uploads/example.pdf"),
        (events[6], content_types[7], "Hansard Minutes", "uploads/example.pdf"),
        (events[11], content_types[6], "Committee Report", "http://www.pmg.org.za/atc131015-report-ad-hoc-committee-protection-state-information-bill-protection-state-information-bill-b-6d-2010"),
        ]

    content = []
    for tmp in content_details:
        item = Content()
        item.event = tmp[0]
        item.type = tmp[1]
        item.title = tmp[2]
        item.url = tmp[3]
        db.session.add(item)
        content.append(item)

    for na_report in na_reports:
        tmp_event, tmp_content = new_report(na_report, b1, stages[1], agents[2], content_types[-1])
        db.session.add(tmp_event)
        db.session.add(tmp_content)

    for ncop_report in ncop_reports:
        tmp_event, tmp_content = new_report(ncop_report, b1, stages[5], agents[3], content_types[-1])
        db.session.add(tmp_event)
        db.session.add(tmp_content)

    db.session.commit()
    return

if __name__ == "__main__":

    rebuild_db()