# FrontDesk AI Requirements Use Cases and Constraints


CIS 457 Senior Design 1 | Team submission | Revised November 26, 2026

Fatkhaziz Mukhamedov, Al Baraa Khaled, Mohammad Abdullah, Amar Al Balkhi

## 1 Purpose and scope

FrontDesk AI is a subscription web service for small businesses. Each business has its own workspace, approved knowledge, staff, services, operating rules and customer requests. A shared receptionist receives questions, answers from approved information, completes supported bookings and sends work that needs a person to the business's staff.

The final system supports a dealership, a salon and a photography studio through the same application. These domains use different intake fields, resources, policies and appointment rules. Universal Motors Group is a dealership stakeholder identified in the earlier requirements. The salon and studio are proposed evaluation scenarios. Their sample records do not represent completed interviews or business agreements.

### Delivery milestones

| Milestone | Required evidence |
| --- | --- |
| Fall 2026 progress milestone | Approximately 20 percent of the overall project, as required by the course. Demonstrate the existing vehicle intake, AI draft, owner review, publication, approved-fact questions and staff inbox. Demonstrate owner AI question preparation, personalized customer requirements, and explained comparison within the dealership. The existing three-domain configuration fixtures are supporting design evidence, not a requirement to complete three live fall businesses. Measure completed work against acceptance tests. |
| Spring 2027 final system | Complete the shared platform, four roles, three domain workflows, appointment management, phone reception, reminders and the dealership functions in Section 6. Demonstrate subscription management in a payment-provider sandbox. |

The November dealership demo is evidence for a subset of the fall workflow. Dates in this specification identify targets and source records. Acceptance targets describe tests to perform and do not claim completed implementation or passed tests. The remaining final-system work stays on the project roadmap.

### Shared functions and domain rules

| Shared platform function | Dealership rules | Salon rules | Photography studio rules |
| --- | --- | --- | --- |
| Approved knowledge and policies | Inventory, warranty, returns, service and lease policies | Service menu, cancellation, deposits and late arrivals | Packages, turnaround, rescheduling and image delivery |
| Appointment lifecycle | Service-bay capacity and vehicle details. Test drives reserve a vehicle and a salesperson. | Service duration, qualified stylist, chair and cleanup buffer | Package duration, photographer, studio or location and setup buffer |
| Requests requiring staff | Appraisal, sales, leasing, title status and repair estimates | Unlisted treatments, corrections and complaints | Custom packages, location approval and special equipment |
| Resource state | Available, reserved or sold vehicle | Stylist and chair availability | Photographer and studio availability |

## 2 Stakeholders users and elicitation

The supplied October 6 document records an October 4 interview with Anwar El Daour of Universal Motors Group conducted by Al Baraa Khaled. It reports missed calls, service and sales questions, paper appointment tracking, after-hours voicemail and concern about cost. These are findings from that supplied record. This revision adds no new interview results.

The professors' annotated AI_Receptionist_Requirements_Notes.pdf is the source of the changes in Appendix A. The team must validate domain rules with representatives before production use. Dr. Liu is the mentor and requirements reviewer. Receipt of written feedback does not establish that a mentor meeting occurred.

### Four user roles

| Role | Permitted goals | Access boundary |
| --- | --- | --- |
| Platform administrator | Create, read, update and deactivate businesses. Assign the first business administrator. Enable allowed shared modules and domain templates. Review platform health and redacted usage. | Platform administration is separately authorized. Access to private business content requires an explicit, audited support session. |
| Business administrator | Manage the business profile, staff invitations and revocation, service rules, approved knowledge, publications, appointments, requests and subscription. | Only the selected business. Cannot grant the platform administrator role. |
| Domain staff or knowledge contributor | Draft knowledge and domain rules for an assigned department. Manage assigned operational records and inquiries. | A department permission determines which records can be edited. Publication and rule activation require business-administrator approval. |
| Customer or general user | Ask questions, read public information, submit requests, book and manage their own appointments. | Public access is bound to the business selected by URL or called number. Private customer actions require a verified link or code. A customer account is optional. |

The existing demo's owner role maps to business administrator. Its staff role is the starting point for domain staff. Platform administration and department permissions require additional implementation.

## 3 Business configuration and operating rules

### Required fields and validation

| Configuration group | Required fields | Validation and effect |
| --- | --- | --- |
| Business identity | Name, unique URL slug, domain template, business time zone, contact email, public address or service-area description | Name 1 to 120 characters. Slug unique. Use a recognized IANA time zone. Parse email syntax. A valid format alone does not prove control. |
| Operating hours | Open or closed for each weekday, open intervals, holiday exceptions | End follows start. Evaluate hours in the business time zone, including daylight-saving changes. |
| Enabled services | Service ID, name, department, duration, resource type, capacity, booking lead time and cancellation window | Duration and capacity are positive. A price is an approved amount or an explicit quote-required flag. Resource allocations cannot exceed capacity. |
| Approved knowledge | At least one approved contact or hours item, source owner, revision and approval | FAQ means a question-and-answer record with question text, answer text, topic, applicable service or domain, revision and approval. Draft items are private. |
| Intake schema | Request type, ordered question IDs, labels, answer types, required flags, choices and validation | Forms differ by service and request type. Required operational facts block automatic completion. A staff inquiry can record missing answers. |
| Staff routing | Department, primary staff destination, optional backup, event recipients and optional callback commitment | A recipient is a same-business user or a verified email/phone destination selected for a named event. No recipient list is inferred from a contact field. |
| Voice channel when enabled | Assigned inbound number, business fallback number, approved greeting and disclosure, forwarding mode | Parse phone numbers with US region rules and store E.164. Require a valid US number pattern. Test a destination before activation to establish reachability. |
| Booking when enabled | Resource schedules, service durations, capacity, booking horizon and minimum lead time | Defaults for test data are a 2-hour lead time and 30-day horizon. The administrator may change them. Appointments must fit working hours and buffers. |
| Notifications when enabled | Event type, channel, recipient, consent where applicable and reminder offsets | Default reminders occur 24 hours before an appointment. Skip offsets already past when a late booking is made. Show delivery state separately from booking state. |

### Services FAQs intake questions and settings

Services are structured offerings such as an oil change, test drive, haircut or portrait session. FAQs are short approved answers to recurring questions. A sample FAQ has question 'What is your cancellation policy?', answer supplied by the business, topic 'cancellation' and service scope 'portrait session'. Different businesses can publish different answers.

Settings are the named fields in the preceding table. They include hours, resource capacity, booking lead time, cancellation policy, transfer destination, backup, notification subscriptions, enabled channels, usage limits and greeting revision. The dashboard displays these fields by name.

| Request type | Intake questions and answer types | Business-specific rule |
| --- | --- | --- |
| Dealership service | Service choice, vehicle year/make/model, preferred time, customer name and contact | Vehicle details and supported service are required for automatic booking. |
| Test drive | Vehicle ID, preferred time, customer name/contact and requested salesperson if any | Selected vehicle must be available. Reserve vehicle and salesperson together. |
| Trade-in | Year/make/model, mileage, stated condition, desired purchase and contact. VIN is optional at inquiry stage. | Appraisal value stays pending until authorized staff enter it. |
| Sales or lease | Vehicle ID, purchase or lease choice, questions and contact | A request records interest. Only staff-approved terms may be displayed. |
| Salon booking | Service choice, preferred stylist or any qualified stylist, time and contact | Check stylist qualification, chair and cleanup buffer. |
| Studio booking | Package, date/time, studio or location, participant count and contact | Check photographer and studio capacity. Unapproved locations need staff review. |
| General message | Question, optional name and contact, preferred contact method | Store only after the visitor chooses to submit or explicitly requests follow-up. |

## 4 Functional requirements for the shared platform

Each FR describes a user goal. Disclosure, classification and greeting are flow steps within FR-05. Tests AT-01 through AT-24 correspond to FR-01 through FR-24.

### FR-01 Manage businesses and modules

The system shall let a platform administrator create, view, update and deactivate businesses, assign their first administrator and enable a permitted set of shared functions and domain modules. Deactivation ends new public interactions and blocks business writes. Deletion requires the configured retention workflow.

AT-01. Given dealership A and salon B, when an administrator enables bookings only for B, B can book and A cannot call the booking API. Deactivating A blocks new A requests without affecting B.

### FR-02 Manage business users and access

The system shall let business administrators invite, assign department permissions to and revoke domain staff in their own business. Protected requests shall verify identity, current role, business and department. Privileged users sign in through managed authentication and MFA. Customers verify control of a contact channel before changing private appointments.

AT-02. Given a revoked staff account, its next protected request is denied. A staff user cannot publish knowledge or grant administrator access. A guessed customer booking reference cannot disclose or change an appointment.

### FR-03 Configure a business and its rules

The system shall let a business administrator maintain the fields in Section 3 without changing application code. Draft changes are validated and previewed before activation. Domain rules and questions are stored by business, service and revision.

AT-03. Given two businesses with different hours, service durations and intake questions, each customer sees only that business's configuration. Saving '555-12' as a routing number fails with a field error.

### FR-04 Publish approved business knowledge and listings

The system shall let authorized staff prepare facts, FAQs, policies and AI-assisted descriptions. Only a business administrator may approve and publish the exact saved revision. New private edits invalidate that revision's approval and preserve the last published snapshot until republication. Unpublishing removes public access.

AT-04. Given a published price of $23,500, saving a private price of $24,500 leaves the public price at $23,500. Approving and republishing the new revision changes it once. Repeating the publish request creates no duplicate.

### FR-05 Obtain an answer or complete a supported request

The system shall let customers reach the selected business through web chat or its configured phone channel, obtain approved information and start an enabled workflow. It shall disclose automated assistance, identify the business, apply that business's approved rules and ask at most two clarifying questions. Unsupported or unresolved requests offer FR-06.

For voice, the approved greeting template includes business name, automated-assistant disclosure and the configured transcription notice before free-form input. An objection stops retained conversational content and offers a human route. Intake steps never grant the model authority to change records.

AT-05. Given identical questions sent to A and B, each answer uses its own published policy. An unknown financing rate produces no invented value. A resolved hours question creates an interaction outcome and no sales lead or inquiry.

### FR-06 Reach staff or leave a follow-up request

The system shall offer a human transfer or an explicitly submitted follow-up request when requested by the customer or needed to complete a goal. It shall follow the request mapping in Section 5, use department routing and record outcome. A successful save and a delivered notification are separate states.

Voice routing rings the primary destination for 20 seconds, then the configured distinct backup for 20 seconds. After hours it follows the business's approved backup rule or offers a message. An immediate-danger report uses an approved emergency message. Transfer failures never cause an automatic sales lead or a promised callback time.

AT-06. Given no answer at either staff destination, the customer may save one follow-up request. If they decline and give no message, only the interaction outcome remains. A callback time is stated only when approved in the business rules.

### FR-07 Manage appointments

The system shall let a customer book, reschedule or cancel an appointment using the selected business's service rules and resource availability. It shall collect service-specific intake, read back the proposed details and require confirmation. The database shall reserve all resources in one transaction and prevent duplicate or conflicting bookings. Rescheduling preserves the original until the replacement is committed.

AT-07. Given ten simultaneous requests for the final available resource, exactly one confirms. Repeating its request key returns the same booking. A failed reschedule preserves the original. A salon service with a 15-minute buffer blocks overlapping reuse.

### FR-08 Review and resolve customer work

The system shall let authorized business staff filter and review interactions, appointments and follow-up requests, update assigned status and add internal notes. The administrator can export their business's permitted records. Knowledge contributors see only their assigned departments.

AT-08. Given a service employee and a sales employee, each sees only assigned private work. A customer cannot access the staff inbox. Status changes persist and identify the actor.

### FR-09 Receive confirmations notifications and reminders

The system shall send configured confirmations for bookings and changes, reminders for upcoming appointments or scheduled service, and staff notifications for assigned events. Each event uses the configured recipient and permitted channel. Retries reuse a unique delivery key and respect opt-out status. A failed notification leaves a committed appointment intact.

AT-09. Given an appointment and a 24-hour reminder rule, the reminder is queued once when due. Re-running the job creates no duplicate. A customer who opted out receives no SMS. A failed delivery is visible to staff.

### FR-10 Activate a business channel

The system shall show channel readiness from required profile fields, approved knowledge, enabled modules and integration tests. Web activation requires a passed public-preview test. Voice activation also requires a correlated incoming test call and greeting confirmation. Booking activation requires working resources and a successful create/cancel test booking. Optional calendar synchronization is tested separately.

AT-10. Given a complete voice profile, the administrator starts a two-minute test window and calls the assigned route. Only a signed provider callback matching business, number, call ID and window plus greeting confirmation passes. Timeout preserves Draft voice status and shows troubleshooting.

### FR-11 Inspect AI requests and audit records

The system shall let authorized administrators inspect AI task time, task type, model, provider response ID when supplied, token usage when supplied, duration, status, business and source revision. It shall record administrative actions, approvals and transactional outcomes with actor and request ID. Unknown provider usage remains unknown.

AT-11. Given a successful draft request and a failed request, both have task records. Each request identifies the saved or published source revision it used. A failure carries a safe category, with no API key or password in logs.

### FR-12 Control usage and subscription access

The system shall enforce business and project usage limits before paid inference and enable modules according to verified subscription state. The final demonstration shall use hosted sandbox checkout and verified provider events. Repeated or older events shall not duplicate charges or restore stale permissions. Card entry occurs on the hosted provider page.

AT-12. Given an exhausted inference allowance, no provider call is made. Given a replayed sandbox subscription event, access changes once. A browser return URL alone grants no feature access.

## 5 Request outcomes and follow-up classification

An interaction records what happened. An inquiry records work that needs follow-up. A sales lead is one inquiry type associated with buying, selling or leasing interest. A successful answer, completed booking or completed transfer does not automatically create an inquiry.

| Reason | Immediate outcome | Follow-up record and creation condition |
| --- | --- | --- |
| Approved hours, price or policy question | Answered | None unless the customer separately requests follow-up |
| Booking or appointment change succeeds | Booked, rescheduled or cancelled | Appointment only. Optional follow-up only when separately requested |
| Buying a vehicle | Sales workflow or approved inventory answer | Sales inquiry when the customer requests contact or a quote |
| Trade-in or leasing | Relevant intake workflow | Trade-in or lease inquiry after confirmed submission |
| Repair quote or unsupported service | Staff review required | Service inquiry after customer agreement |
| Unknown question | Handoff offered | General inquiry only after customer agrees and confirms the message |
| Staff transfer succeeds | Transferred | No new inquiry unless staff explicitly create one |
| Transfer or booking cannot complete | Follow-up offered | Callback or appointment request after customer agrees |
| Unclear request after two clarifications | Unresolved | General inquiry if accepted. Otherwise interaction only |
| Customer disconnects | Abandoned | No inferred lead. Preserve an incomplete request only after explicit submission consent |

Inquiry fields are business, department, type, reason, optional listing/service, submitted answers, message, name if provided, contact and verification state, priority, source interaction, request key and status. Statuses are New, Pending, Resolved and Closed. The existing demo's Open maps to New in the migration. Missing contact is allowed for a saved message, but the customer is told that a direct reply requires contact details.

## 6 Functional requirements for business domains

### FR-13 Manage dealership inventory

The system shall let dealership staff create and maintain stock ID, vehicle year/make/model, mileage, price, availability and optional VIN, power, fuel type and fuel-efficiency facts. The business administrator approves public changes. Reservations and completed sales or leases update stock availability consistently.

AT-13. Given a sold vehicle, new test-drive reservations are refused. An unapproved stock-price edit does not affect public answers. Unknown specification fields remain empty.

### FR-14 Compare vehicles

The system shall compare two to four published vehicles from the same dealership using approved price, mileage, power, fuel type and fuel-efficiency fields. It shall display units and identify missing values.

AT-14. Given two cars with different published values and one missing power figure, the comparison matches the records and shows power as unknown for that car. Private inventory never appears.

### FR-15 Manage trade-in requests

The system shall collect vehicle details, mileage, customer-stated condition, optional VIN, contact and associated purchase interest, and route the request for appraisal. Authorized staff record appointment, appraised amount, notes and customer decision through Submitted, Under review, Appraised, Accepted, Declined or Withdrawn states.

AT-15. Given a submitted trade-in, the customer sees a reference and pending appraisal. Only authorized staff may enter an appraised amount. An accepted trade-in can be linked once to a sale record.

### FR-16 Manage test drives and walk-ins

The system shall let customers request a specific vehicle and time and let staff record walk-ins. Confirmation reserves both an available vehicle and a qualified salesperson. A walk-in is assigned immediately only when both are available, otherwise staff offer a later slot or a waiting request.

AT-16. Given a reserved vehicle, a conflicting walk-in is not confirmed. Releasing a cancelled test drive restores both resources once.

### FR-17 Manage vehicle sales

The system shall track a vehicle sale from customer interest through staff quote, reservation, completed sale or cancellation. Quotes record the vehicle, approved price, itemized staff-entered fees, optional trade-in reference, expiry and staff approval. Completion records an externally completed transaction reference and marks the vehicle sold in the same database transaction.

AT-17. Given a sale completed by authorized staff, the vehicle becomes sold once. Replaying completion does not duplicate the sale. A customer request or AI draft cannot mark a sale complete.

### FR-18 Manage vehicle leases

The system shall record a lease inquiry and a staff-approved proposal with vehicle, term, annual mileage allowance, upfront amount, monthly amount, included fees, expiry and policy references. Staff maintain Draft, Approved, Accepted, Completed or Cancelled state. Completion records an external agreement reference and removes that vehicle from available stock.

AT-18. Given no approved monthly amount, the assistant offers staff follow-up. Published lease terms match the approved proposal. Completing a lease cannot race a sale for the same vehicle.

### FR-19 Track titles and registration

The system shall track a title/registration case linked to a sale or lease, with document checklist, responsible staff, due date, customer-visible status and external submission reference. Supported statuses are Awaiting documents, Ready for staff review, Submitted, Completed and Needs correction. Staff control state changes.

AT-19. Given a missing document, the case identifies it and stays awaiting documents. Only a verified customer or authorized staff can view the case. Completion requires an external reference entered by staff.

### FR-20 Manage dealership service

The system shall let staff maintain a service catalogue, book bay or advisor capacity, record requested work and vehicle, and track Requested, Scheduled, In progress, Awaiting customer, Completed or Cancelled service work. Staff approve estimates before the receptionist can quote them. The customer can request service-status updates after verification.

AT-20. Given an unapproved repair estimate, the customer gets a staff-review response. A completed service can schedule a reminder using the business's approved interval.

### FR-21 Answer business policy questions

The system shall use versioned, approved policy records scoped to business, service or inventory item, including warranty, returns, deposits, cancellations and applicable lease terms. It shall show effective date and any stated limitations. Uncovered cases are sent for staff review.

AT-21. Given different return policies for two dealerships, each customer's answer cites the correct policy revision. Expired or draft policy text is not used.

### FR-22 Manage salon services

The system shall let salon administrators configure services, prices or quote flags, durations, cleanup buffers, qualified stylists, chairs and cancellation rules. Customers can obtain approved information and manage appointments using those rules.

AT-22. Given a 45-minute haircut with a 15-minute buffer, the same chair cannot be booked during the full hour. An unqualified stylist is not offered for that service.

### FR-23 Manage photography services

The system shall let studio administrators configure packages, durations, setup buffers, photographers, studio resources, participant limits, approved locations, deliverables and turnaround policies. Requests for unapproved locations or custom deliverables go to staff.

AT-23. Given a two-hour studio package and a 30-minute setup buffer, the photographer and studio are reserved consistently. An outdoor location requiring approval produces a request instead of an automatic confirmation.

### FR-24 Publish events and manage free registration

The system shall retain the planned event workflow as an enabled module. Administrators publish approved event facts and admission rules, and customers register or cancel within configured capacity. Repeated requests use a unique key and cancellation releases places once.

AT-24. Given one place remaining and concurrent registrations, exactly one place is committed. Repeating a cancellation does not release an extra place.

Sale, lease and title management cover intake, approved information, staff workflow and status tracking. Payment processing for vehicles, credit decisions, contract signatures and direct government submissions remain external business operations, represented by staff-entered references.

## 7 Nonfunctional requirements and verification targets

| ID | Target | Verification |
| --- | --- | --- |
| NFR-01 Tenant and role isolation | All private actions enforce business, role and department. Secrets and passwords stay out of application records, prompts and browser bundles. | At least 40 prepared cross-business, cross-role and anonymous read/write attempts across three domain fixtures must all be denied. Inspect build and logs. |
| NFR-02 Authentication | Verified privileged identities use MFA, expire after 30 minutes idle, and are throttled for 15 minutes after five failed attempts per account and source window. | Correct password without the second factor fails privileged access. Test revocation, idle expiry and throttling with controlled identities. |
| NFR-03 Approved-fact behavior | At least 90 percent correct request classification and 90 percent correct answers on supported inputs. No unsupported factual value is displayed. | Freeze a set of 60 classified requests, 30 approved questions and 20 unknown/hostile questions before testing. Two reviewers independently score outputs. |
| NFR-04 Web response | Ordinary API p95 below 1 second at 10 concurrent users. Show AI waiting state within 1 second and apply a 35-second shopping-provider timeout. | Measure 200 ordinary requests and 30 AI requests on the recorded deployment. Report provider latency separately. |
| NFR-05 Voice response and capacity | Target three simultaneous calls per enabled business, answer within 3 seconds and reply audio within 2 seconds of end-of-turn for 95 percent of turns. | Test 50 calls with at least 300 turns and ten three-call concurrency rounds. Record end-of-turn and first-audio timestamps. Performance remains to be measured. |
| NFR-06 Transaction reliability | Retries never duplicate a booking, inquiry, sale, lease or registration. Capacity and vehicle state remain consistent. | Ten concurrent final-resource requests, repeated request keys and injected failures at each commit boundary produce the expected single outcome. |
| NFR-07 Privacy and retention | Transcripts and question content expire after 30 days. Inquiry contact data expires 90 days after closure. Redacted task metadata and audit events expire after 90 days. | Backdate fixtures and run purge jobs. Retained counts contain no content. Record provider/backups retention separately and verify the chosen backup policy before deployment. |
| NFR-08 Accessibility and usability | Keyboard operation, visible labels/focus and understandable errors. Four of five nontechnical participants complete business setup within 20 minutes using a prepared scenario. | Record versions, completion times and problems. Test the core flow on laptop and phone widths in Safari and Chrome. |
| NFR-09 Service recovery | Target 99 percent monthly availability for enabled reception channels, with failures measured and fallback routes tested. | One-minute monitoring and a documented observation period. Ten forced voice failures reach configured fallback. No availability result is claimed before measurement. |
| NFR-10 Evidence and maintainability | One repository, pinned dependencies, versioned migrations and reproducible setup. Every paid AI attempt has an inspectable task outcome. | A teammate starts from a clean checkout. Tests use mocks by default. Separately record funded integration checks and remaining limits. |

## 8 Brief use case descriptions and traceability

| Use case | Actor goal | Requirements and tests |
| --- | --- | --- |
| UC-01 | Platform administrator manages businesses and enabled modules | FR-01 / AT-01 |
| UC-02 | Business administrator manages users and permissions | FR-02 / AT-02 |
| UC-03 | Administrator configures rules and activates channels | FR-03, FR-10 / AT-03, AT-10 |
| UC-04 | Staff draft content and administrator approves publication | FR-04 / AT-04 |
| UC-05 | Customer obtains an answer or starts a supported request | FR-05, FR-21 / AT-05, AT-21 |
| UC-06 | Customer reaches staff or submits follow-up | FR-06 / AT-06 |
| UC-07 | Customer manages an appointment | FR-07 / AT-07 |
| UC-08 | Staff review and resolve assigned work | FR-08 / AT-08 |
| UC-09 | Customer or staff receives configured messages | FR-09 / AT-09 |
| UC-10 | Administrator inspects task evidence and usage | FR-11, FR-12 / AT-11, AT-12 |
| UC-11 | Dealership manages inventory and comparisons | FR-13, FR-14 / AT-13, AT-14 |
| UC-12 | Customer submits trade-in and staff appraise | FR-15 / AT-15 |
| UC-13 | Customer or staff arranges a test drive or walk-in | FR-16 / AT-16 |
| UC-14 | Staff manage a sale or lease | FR-17, FR-18 / AT-17, AT-18 |
| UC-15 | Staff track title and registration work | FR-19 / AT-19 |
| UC-16 | Customer and staff manage dealership service | FR-20 / AT-20 |
| UC-17 | Customer books a salon or photography service | FR-22, FR-23 / AT-22, AT-23 and AT-07 |
| UC-18 | Customer registers for a free event | FR-24 / AT-24 |

NFR-01 and NFR-02 apply to every private use case. NFR-03 applies to UC-04 through UC-06, UC-11 and policy answers. NFR-06 applies to all writes. NFR-07 applies to every retained interaction. Remaining NFRs apply to their named channel or interface.

## 9 Fully developed use cases

### UC-03 Configure and activate a business

Actor and trigger. A business administrator accepts an invitation and begins setup. Supporting actors are managed authentication, optional calendar synchronization and the voice provider when voice is enabled.

Preconditions. The platform administrator created the business, selected its domain template and enabled modules. The business administrator is authenticated with the required assurance level.

1. The administrator enters the identity, time zone, hours, service menu and required contact fields in Section 3. The system validates each named field and saves a private configuration revision.
2. The administrator assigns resources, intake schemas and department permissions. The system previews the questions for each selected service.
3. The administrator reviews FAQ/policy answers, selects event recipients and routing destinations, and approves a greeting composed from the business name, selected welcome text and required disclosure.
4. The system lists enabled web, booking, voice and notification features with Ready, Disabled or Needs setup status and the exact missing prerequisite.
5. For web, the administrator runs a preview question. For booking, the system creates and cancels a test reservation. A calendar sync test uses a marked event in the selected calendar when synchronization is enabled.
6. For voice, the system shows the assigned inbound number and carrier-specific forwarding guidance. The administrator configures forwarding with their own carrier, starts a timed test and calls the business number.
7. The system associates a signed incoming webhook with the assigned number, business and test window, records provider call ID and greeting playback event, and asks the administrator to confirm that the greeting was heard.
8. The administrator activates each ready channel. The system records the configuration revision and an audit event, then displays the enabled functions by name.

Success. The selected channels are active with a tested configuration. Disabled or incomplete channels remain visibly unavailable.

Exceptions. Invalid or missing required fields block the affected channel. A calendar failure leaves synchronization pending while internal booking can remain active. No matched voice callback within two minutes marks the test timed out. Missing greeting confirmation keeps voice in Draft. A provider webhook alone cannot prove the administrator heard the correct audio. Profile edits after a failed test require a fresh test of the changed channel.

### UC-07 Book reschedule or cancel an appointment

Actor and trigger. A customer selects an available service through web or voice. Supporting actors are the business resource scheduler and delivery provider.

Preconditions. Booking is enabled, service rules and resources are active, and the selected business is identified. Changing an existing appointment also requires a verified management link or contact code.

1. The customer identifies the service and answers its configured questions. The system rejects unsupported selections and identifies missing required facts.
2. The customer gives a preferred time. The system offers up to three available times in the business time zone, considering duration, buffer, staff skills and resource capacity.
3. The customer selects a time and confirms the summary, including service, resource where relevant, date, time and contact.
4. The backend validates the request key and reserves all resources in one transaction. It rechecks capacity under locks before committing.
5. After commit the customer receives a booking reference. Confirmation and reminder delivery are queued independently with recorded consent.
6. For rescheduling, the system verifies the customer, locks old and proposed allocations in a fixed order and commits the new allocation and release together. For cancellation it verifies the same authority and releases the allocation once.

Success. Exactly one confirmed appointment occupies the expected resources. A cancelled booking releases capacity once.

Exceptions. A stale slot returns alternative times. A failed write confirms nothing. A failed reschedule preserves the old booking. An SMS or calendar-sync failure does not cancel the database booking. A customer who cannot verify control receives a staff-review option without disclosure of the stored appointment.

### UC-06 Reach staff or submit follow-up

Actor and trigger. A customer asks for a person or accepts follow-up after an unsupported or incomplete request.

Preconditions. The business is identified and the relevant routing/intake revision is approved.

1. The system determines the reason using Section 5. A resolved FAQ or completed booking ends with its own outcome.
2. For a requested phone transfer, the system checks hours and department rules, announces transfer and calls the primary then distinct backup destination with the defined timeouts.
3. If transfer is unavailable, or for web handoff, the customer chooses whether to send a request. The system asks the intake questions for that request type and confirms any callback contact.
4. The customer reviews the summary. On confirmation the backend saves one inquiry using the request key and source interaction.
5. The system reports that the request was saved. A separate delivery event records whether staff notification was queued, delivered or failed.
6. Assigned staff view the inquiry, update status and record their follow-up. The customer receives only an approved callback commitment when one exists.

Success. The customer reaches staff or creates an explicitly submitted request visible to the correct department.

Exceptions. Declining follow-up creates no inquiry. Missing contact does not become verified contact. A failed save shows retry and no success message. Notification failure preserves the saved request. An emergency invokes the approved emergency message and configured escalation without attempting a sales workflow.

### UC-04 Review and publish business content

Actor and trigger. A staff contributor saves a draft and a business administrator opens it for approval. The optional AI service supplies editable proposed wording.

Preconditions. The record belongs to the selected business. Required fields and domain validation are available.

1. Staff enter facts or a policy answer. The system saves a private revision and labels unknown facts.
2. If the user requests AI drafting, the backend checks usage, sends only permitted facts and records the provider outcome. The result remains an editable draft.
3. The administrator reviews the saved facts, wording and source revision and explicitly approves that revision.
4. In one transaction the backend checks current permissions and revision, saves the public snapshot and records approval/publication evidence.
5. The interface displays the public URL. Public answers use that published snapshot and revision.

Success. One approved revision is public. Private changes cannot alter current customer answers.

Exceptions. Concurrent edits require fresh review. A staff publication attempt is denied. AI failure preserves the existing draft. A repeated request returns the same publication. Unpublishing stops public retrieval and future answers from the record.

## 10 Constraints assumptions and delivery checks

The planned stack remains React and TypeScript, Python FastAPI, Supabase PostgreSQL/Auth/storage, and server-side xAI requests. A hosted deployment is the final delivery target. The Mac-hosted application remains the current demo environment. A worker handles reminders, notifications, retention and provider reconciliation when those workflows are implemented.

Internal database reservations are the booking authority. Google Calendar synchronization is a separate adapter that can be demonstrated using a selected calendar. Voice uses a programmable provider adapter and requires a funded number and tested audio integration. The existing text-model integration does not prove a voice integration.

English and US phone numbers are the initial language/region constraints. The existing $5 xAI purchase is the authorized AI budget. Model IDs and provider availability must be verified from the account at integration time. Additional hosting, voice, messages or recurring services require a concrete cost decision before purchase. No new paid service is assumed by this revision.

Before final acceptance, configure three domain fixtures, obtain review of the operating rules, verify deployment and test AT-01 through AT-24 and NFR-01 through NFR-10. Real provider checks must be recorded separately from mock tests. The current fall work continues before additional final-system implementation is started.

## Appendix A Feedback resolution

| Feedback in annotated PDF | Resolution in this revision |
| --- | --- |
| Pages 1 and 3. Single dealership pilot is insufficient | Sections 1 and 6 require shared functions and three distinct domains. The dealership remains an example and stakeholder. |
| Page 1. Per-business rules above shared functionality | Section 3 defines business, service, department and revision scope. FR-01, FR-03, FR-22 and FR-23 make differences testable. |
| Page 1. System administrator, business administrator, domain user and general user | Section 2 gives four roles, CRUD goals and access boundaries. FR-01 and FR-02 enforce them. |
| Page 1. Is a general user business specific | Section 2 binds each public session to the selected URL or called number. Private operations require verified authority. |
| Pages 1 and 2. Trade-ins, test drives/walk-ins, inventory, comparisons, sales, leases, titles, service, policies and reminders | FR-09 and FR-13 through FR-21 define each workflow and a corresponding test. |
| Pages 2 and 7. Merge call steps into goal requirements | FR-05 covers reception and supported completion. FR-06 covers human assistance. Disclosure and classification remain steps within the flows. |
| Page 17. Reasons, lead types and calls that are not leads | Section 5 maps reasons to outcomes. UC-06 requires explicit submission and separates interactions from inquiries. |
| Page 18. What are services and FAQs and in what format | Section 3 specifies structured service fields and versioned question/answer records with examples. |
| Page 18. Are questions shared across services/businesses | Intake schemas are keyed by business, request type and service. The examples differ across three domains. |
| Page 18. Meaning of intake questions, recipients and settings | Section 3 names question types and required flags, event-recipient pairs and each configurable setting. |
| Page 19. Forwarding instructions and greeting source | UC-03 uses assigned provider number, carrier-specific guidance and administrator-approved greeting template. |
| Page 19. Which features become live | FR-10 and UC-03 display readiness separately for web, booking, voice, notifications and optional synchronization. |
| Page 19. Required fields and number validation | Section 3 lists required fields and validation. Pattern validity and tested reachability are distinguished. |
| Page 19. How is a missing test call detected | FR-10 and UC-03 define a two-minute window, signed callback, assigned number, business, provider call ID and greeting confirmation. |

### Previous requirement identifiers

The annotated phone document's FR1 through FR4 map to FR-05. FR5 and FR6 map to FR-07. FR7 and FR8 map to FR-06. FR9 and FR10 map to FR-09. FR11 maps to FR-08. FR12 maps to FR-03 and FR-04. FR13 maps to FR-10. FR14 maps to FR-01 and FR-02.

The October web specification's FR-ACC family maps to FR-01, FR-02 and FR-12. FR-LST maps to FR-04, FR-13 and FR-24. FR-REC maps to FR-05 and FR-11. FR-HND maps to FR-06 and FR-08. FR-SCH maps to FR-07 and FR-24. FR-BIL maps to FR-12. This revision supersedes the narrower single-domain final-scope statements in those earlier documents.

## Appendix B Sources

Professors' annotated AI_Receptionist_Requirements_Notes.pdf, 22 pages, supplied through Blackboard and reviewed November 19, 2026.

FrontDesk AI Requirements Use Cases and Constraints, October 22, 2026. FrontDesk AI Detailed System Design, revised October 28, 2026. The current feasibility-demo repository and presentation handoff at commit d73c2c4896967e3d913116567fa9b7504d350c31 were inspected for implementation status.
## 11 Fall AI additions and release boundaries

These additions retain FR-01 through FR-24 and the full multi-business final scope. Faculty feedback dated November 2026 remains binding on the final system. The November 24 discussion with Dr. Matovu prioritizes a dealership and a concrete AI feature for the fall showcase. A working vertical slice is the course's 20 percent milestone; test counts are not a calculation of overall project completion.

### FR-25 Prepare owner knowledge using AI

The system shall let a business administrator explicitly request likely customer questions and information gaps from published business and inventory context. Suggestions remain private and unapproved. The owner supplies a supported answer, routes the question to staff, or ignores it. Saving and exact-revision publication are separate actions. The model cannot publish or create an approved answer.

AT-25. Generate suggestions from published context, verify unpublished draft text is absent from the outgoing payload, save questions privately, add a verified answer, approve the saved revision and publish. The answer then becomes public; unanswered, draft and ignored cards do not.

### FR-26 Hold a personalized shopping conversation

The system shall interpret explicit customer needs into editable vehicle-price/total budget, minimum seats, mileage ceiling, requested specifications, required features and soft priorities. It shall preserve requirements across accepted turns unless the customer changes them, ask one relevant follow-up, explain selected-vehicle trade-offs and recommend only published available vehicles meeting all known hard constraints. Missing required facts cannot qualify as a verified match. The system shall show the source records used and offer a consented staff inquiry without silently submitting one.

AT-26. Send a vehicle-price budget of $25,000 and a five-seat requirement, then explicitly raise the budget to $30,000. Verify preferences and selected IDs in both HTTP requests, cited published revisions and deterministic eligibility. Ask whether a price is fair; the answer must distinguish known asking prices from unknown external market/condition evidence. Unsupported values, foreign source IDs and a changed publication during the request fail safely. Validate using real xAI separately from mocked regressions.

### UC-19 Prepare and publish AI-assisted owner knowledge

Actor: business administrator. Trigger: the owner wants to prepare for customer questions. Preconditions: verified owner membership; business identified; published context available; spending allowance sufficient for an explicitly requested AI action.

1. The owner requests suggestions once. The backend reserves an attempt and conservative cost, stores task intent, and sends published context to xAI. It does not send unapproved question drafts.
2. The system validates question shape, length and duplicate rules, records provider and application outcomes, and displays private unsaved questions.
3. The owner supplies true answers and a source note, marks staff-only questions or ignores irrelevant suggestions. Editing clears approval.
4. The owner saves the private cards with expected_revision. The server rejects conflicting edits instead of overwriting another revision.
5. The owner reviews the saved cards, confirms approval and publishes that exact revision. Only approved answered cards or deliberate staff routes are exposed publicly.
6. Public answers use the published snapshot; later private edits leave it unchanged. The owner can unpublish knowledge.

Success: the business has approved, traceable published knowledge and private information gaps. Minimal guarantee: failed inference or save cannot change public content. Exceptions: insufficient allowance sends no provider request; malformed output stays unaccepted; stale revision requires reload; staff role cannot approve; a failed provider response is recorded without automatic retry.

### UC-20 Personalize and compare published options with AI

Actor: customer. Trigger: the customer describes needs or asks a follow-up about selected vehicles. Preconditions: the selected business has published inventory; at most three selected IDs belong to it; AI is configured and the shared allowance permits the call.

1. The customer enters a natural request or sets the visible requirements. The browser sends the message, accepted conversation history, typed preferences and selected IDs to the business-scoped endpoint.
2. The backend validates the input, resolves only published records, assembles revision-specific sources and reserves usage in one transaction before contacting xAI.
3. xAI returns structured preferences, an explanation, one follow-up, recommended listing IDs and cited source IDs. It has no database-write or booking authority.
4. The backend validates shape, source membership, explicit changes to requirements, hard constraints, permitted numeric claims and supported arithmetic. Inline citations and list positions are separated from factual quantities. A new read checks that the published snapshot is still current.
5. Accepted preferences become visible and editable. The customer sees the explanation, sources and suggested matches. A factual comparison table remains available independently of AI.
6. The customer changes a requirement and sends another explicit turn. The system carries forward earlier accepted requirements and does not invent a successful turn after a rejected response.
7. If staff help is wanted, the customer reviews the summary/selected vehicles, supplies contact separately, consents and submits one inquiry. The staff inbox stores the preferences and published snapshots.

Success: an accepted, source-linked explanation helps the customer narrow options and records a verifiable provider request. Minimal guarantee: a rejected completion changes no facts, preferences or business records. Exceptions: expired/unpublished selections require refresh; stale publication returns conflict; missing total-cost fees prevent a certified total-budget match; unavailable inference offers facts and staff help; no retry occurs automatically. Postcondition: chatting alone creates no sales lead or inquiry.

### Additional brief use cases

| ID and name | Actor goal | Requirements | Delivery |
| --- | --- | --- | --- |
| UC-19 Prepare and publish AI-assisted owner knowledge | Owner finds questions, supplies answers and approves publication | FR-04, FR-25 | Fall |
| UC-20 Personalize and compare published options with AI | Customer refines needs and receives cited option trade-offs | FR-05, FR-14, FR-26 | Fall live acceptance required |
| UC-21 Manage subscription access | Business administrator uses hosted sandbox checkout; verified events control enabled modules | FR-12 | Spring |
| UC-22 Manage privacy and retention | Authorized administrator exports or removes permitted customer content under the retention policy | NFR-07 | Spring |

### Clarified measurable targets

The actual shopping provider timeout is 35 seconds; legacy calls use 30 seconds. NFR-04 is revised to a 35-second provider timeout for shopping, plus a visible waiting state within one second and no automatic paid retry. The p95 latency targets require a recorded deployment benchmark and are not results of unit tests. NFR-02 MFA, department roles and explicit idle throttling remain final-system acceptance targets, not current controls. NFR-07 deletion schedules remain planned; metadata minimization is implemented but is not a purge job.

For the fall AI slice add NFR-11: zero provider requests occur on navigation, comparison, status refresh or a rejected budget reservation; prove this with mocked transport counts. Add NFR-12: preparation reservations must not exceed $1.00 from the owner-declared $4.97 remaining allowance and must preserve at least $3.50 while preparation mode is active. Failed attempts remain reserved, the historical counter is never reset, and an unpriced model is blocked until the estimate is reviewed. These figures are application ceilings, not a reading of the current xAI balance.
