// RFS23-13522 - Site Tracking Project
/**
 * @description Apex controller for the portalTracker LWC. Handles creation of
 * Portal_Analytics__c records from both LWC and Flow contexts. Runs without sharing
 * to support guest user writes on Experience Cloud.
 */
public without sharing class PortalTrackingController {

    // --- Invocable / AuraEnabled input wrapper ---

    /**
     * @description Input parameters for createEvent. Shared wrapper used by both
     * the LWC (@AuraEnabled) and Flow (@InvocableMethod) entry points to pass
     * session context, page metadata, and user agent data for a single tracking event.
     */
    public class PortalEventInput {
        @AuraEnabled @InvocableVariable(label='Session ID' required=true)
        public String sessionId;

        @AuraEnabled @InvocableVariable(label='Page Name')
        public String pageName;

        @AuraEnabled @InvocableVariable(label='Page URL')
        public String pageUrl;

        @AuraEnabled @InvocableVariable(label='Referrer URL')
        public String referrerUrl;

        @AuraEnabled @InvocableVariable(label='Event Type')
        public String eventType;

        @AuraEnabled @InvocableVariable(label='Search Term')
        public String searchTerm;

        @AuraEnabled @InvocableVariable(label='Knowledge Article ID')
        public String recordId;

        @AuraEnabled @InvocableVariable(label='Knowledge Article URL Name')
        public String urlName;

        @AuraEnabled @InvocableVariable(label='Device Type')
        public String deviceType;

        @AuraEnabled @InvocableVariable(label='Screen')
        public String screen;

        @AuraEnabled @InvocableVariable(label='Browser')
        public String browser;

        @AuraEnabled @InvocableVariable(label='OS')
        public String os;

        @AuraEnabled @InvocableVariable(label='User ID')
        public String userId;

        @AuraEnabled @InvocableVariable(label='Logged In As User Session')
        public Boolean isInternal;

        @AuraEnabled @InvocableVariable(label='Viewport')
        public String viewport;

        @AuraEnabled @InvocableVariable(label='Language')
        public String language;

        @AuraEnabled @InvocableVariable(label='Time Zone')
        public String timeZone;
    }

    // Overridden in tests to avoid uncatchable System.UnexpectedException from
    // Auth.SessionManagement.getCurrentSession() when no real session exists.
    @TestVisible
    private static Map<String, String> testSessionMap = null;

    // Overridden in tests to exercise the network-name branches of resolveEnvironment()
    // without requiring an actual Experience Cloud network context.
    @TestVisible
    private static String testNetworkName = null;

    private static Map<String, String> fetchSession() {
        if (Test.isRunningTest()) {
            return testSessionMap;
        }
        return Auth.SessionManagement.getCurrentSession();
    }

    // --- LWC entry point ---

    /**
     * @description Creates a Portal_Analytics__c record from the portalTracker LWC.
     * When a Knowledge recordId is provided, queries the article to determine
     * whether the event type is Article Viewed or Collection Viewed.
     * @return Id of the inserted Portal_Analytics__c record.
     */
    @AuraEnabled
    public static Id createEvent(
        String sessionId,  String pageName,
        String pageUrl,    String referrerUrl,    String eventType,
        String searchTerm, String recordId,       String urlName,
        String deviceType, String screen,         String browser,
        String os,         String userId,         Boolean isInternal,
        String viewport,   String language,       String timeZone
    ) {
        PortalEventInput input = new PortalEventInput();
        input.sessionId              = sessionId;
        input.pageName               = pageName;
        input.pageUrl                = pageUrl;
        input.referrerUrl            = referrerUrl;
        input.eventType              = eventType;
        input.searchTerm             = searchTerm;
        input.recordId               = recordId;
        input.urlName                = urlName;
        input.deviceType             = deviceType;
        input.screen                 = screen;
        input.browser                = browser;
        input.os                     = os;
        input.userId                 = userId;
        input.isInternal             = isInternal;
        input.viewport               = viewport;
        input.language               = language;
        input.timeZone               = timeZone;
        return insertEvent(input);
    }

    /**
     * @description Checks whether the current authenticated session originates from a known
     * Returns false for guest users and any session where the session cannot be determined.
     * @return True if session signals indicate an internal user logged in as a portal user.
     */
    @AuraEnabled
    public static Boolean isInternalSession() {
        if (UserInfo.getUserType() == 'Guest') {
            return false;
        }
        try {
            Map<String, String> session = fetchSession();
            if (session == null) {
                return false;
            }
            // ParentId non-null: child of an admin session — definitive "Login As" signal.
            if (String.isNotBlank(session.get('ParentId'))) {
                return true;
            }
            // LoginType "Unknown": Login As sessions have no recognized login type.
            if ('Unknown'.equals(session.get('LoginType'))) {
                return true;
            }
            // UserType "Standard": internal Salesforce user, not a community user.
            if ('Standard'.equals(session.get('UserType'))) {
                return true;
            }
            return false;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * @description Debug method — returns the full Auth.SessionManagement session map as JSON
     * so all available keys can be inspected in browser sessionStorage via DevTools.
     * @return JSON string of the session map, or null for guests.
     */
    @AuraEnabled
    public static String getClientIp() {
        if (UserInfo.getUserType() == 'Guest') {
            return null;
        }
        try {
            Map<String, String> session = fetchSession();
            return session != null ? JSON.serialize(session) : null;
        } catch (Exception e) {
            return null;
        }
    }

    /**
     * @description Retroactively sets Logged_In_As_User_Session__c = true on a single
     * Portal_Analytics__c record. Called by portalTracker when the VPN check resolves
     * after the first page event was already written.
     * @param eventId Id of the Portal_Analytics__c record to update.
     */
    @AuraEnabled
    public static void updateEventInternalFlag(Id eventId) {
        if (eventId == null) {
            return;
        }
        Database.update(
            new Portal_Analytics__c(Id = eventId, Logged_In_As_User_Session__c = true),
            false,
            AccessLevel.SYSTEM_MODE
        );
    }

    /**
     * @description Stamps Related_Articles_Found__c = true on the most recent
     * Portal_Analytics__c record for the given session and page URL.
     * Called by the relatedArticles LWC after its wire resolves with results.
     * @param sessionId Session ID from sessionStorage.
     * @param pageUrl Current page URL used to locate the matching event record.
     */
    @AuraEnabled
    public static void updateRelatedArticlesFound(String sessionId, String pageUrl) {
        if (String.isBlank(sessionId) || String.isBlank(pageUrl)) {
            return;
        }
        List<Portal_Analytics__c> events = [
            SELECT Id FROM Portal_Analytics__c
            WHERE Session_ID__c = :sessionId AND Page_URL__c = :pageUrl
            WITH SYSTEM_MODE
            ORDER BY CreatedDate DESC
            LIMIT 1
        ];
        if (events.isEmpty()) {
            return;
        }
        Database.update(
            new Portal_Analytics__c(Id = events[0].Id, Related_Articles_Found__c = true),
            false,
            AccessLevel.SYSTEM_MODE
        );
    }

    // --- Flow entry point ---

    /**
     * @description Invocable entry point for Flow. Accepts a list to support
     * bulk invocation patterns; processes the first input only for screen flows.
     * @param inputs List of PortalEventInput from Flow.
     */
    @InvocableMethod(label='Track Portal Event' category='Portal Tracking')
    public static void trackEvent(List<PortalEventInput> inputs) {
        if (inputs == null || inputs.isEmpty()) return;
        insertEvent(inputs[0]);
    }

    // --- Private ---

    /**
     * @description Resolves the Amplify environment for the current request context.
     * Returns null when Network.getNetworkId() returns null (standard Salesforce UI context),
     * which causes the field to be left blank rather than defaulting to a portal value.
     */
    private static String resolveEnvironment() {
        String networkName;
        if (Test.isRunningTest() && testNetworkName != null) {
            networkName = testNetworkName;
        } else {
            Id networkId = Network.getNetworkId();
            if (networkId == null) {
                return 'Amplify Salesforce';
            }
            List<Network> networks = [SELECT Name FROM Network WHERE Id = :networkId WITH SYSTEM_MODE LIMIT 1];
            if (networks.isEmpty()) {
                return 'Amplify Salesforce';
            }
            networkName = networks[0].Name;
        }
        if (networkName == 'Amplify Customer Portal') {
            return 'Amplify Customer Portal';
        }
        if (networkName == 'Amplify Internal Support') {
            return 'Amplify Internal Support';
        }
        return 'Amplify Salesforce';
    }

    private static Id insertEvent(PortalEventInput input) {
        String  resolvedEventType   = input.eventType;
        Id      knowledgeId         = null;
        Integer knowledgeVersionNum = null;

        // 'Program Link' is a marker from helpCenterProgramsListLWR indicating the
        // base event type should be resolved normally (Article/Collection Viewed)
        // and then suffixed with ' (Program Link)'.
        Boolean appendProgramLink = resolvedEventType == 'Program Link';
        if (appendProgramLink) {
            resolvedEventType = null;
        }

        // When a Knowledge identifier is present, query the article to determine
        // whether this is an article or collection view. Prefer recordId; fall
        // back to UrlName for Experience Cloud pages that expose only the slug.
        Boolean hasKnowledgeRef = (String.isBlank(resolvedEventType) || resolvedEventType == 'Article Translation Viewed' || resolvedEventType == 'Related Article Viewed')
            && (String.isNotBlank(input.recordId) || String.isNotBlank(input.urlName));

        if (hasKnowledgeRef) {
            List<Knowledge__kav> articles = String.isNotBlank(input.recordId)
                ? [SELECT Id, VersionNumber, Article_is_Collection__c FROM Knowledge__kav WHERE Id = :input.recordId WITH SYSTEM_MODE LIMIT 1]
                : [SELECT Id, VersionNumber, Article_is_Collection__c FROM Knowledge__kav WHERE UrlName = :input.urlName AND PublishStatus = 'Online' WITH SYSTEM_MODE LIMIT 1];

            if (!articles.isEmpty()) {
                if (String.isBlank(resolvedEventType)) {
                    resolvedEventType = articles[0].Article_is_Collection__c ? 'Collection Viewed' : 'Article Viewed';
                }
                knowledgeId         = articles[0].Id;
                knowledgeVersionNum = articles[0].VersionNumber;
            } else {
                if (String.isBlank(resolvedEventType)) {
                    resolvedEventType = 'Page Viewed';
                }
            }
        }

        if (appendProgramLink) {
            resolvedEventType = (resolvedEventType != null ? resolvedEventType : 'Page Viewed') + ' (Program Link)';
        }

        // Knowledge article titles are high-cardinality and not useful as a page name
        // bucket; report a generic label instead whenever the event resolved to a
        // specific Knowledge article/collection.
        String resolvedPageName = knowledgeId != null ? 'Knowledge Article' : input.pageName;

        Portal_Analytics__c event = new Portal_Analytics__c(
            Session_ID__c                         = input.sessionId,
            Page_Name__c                          = resolvedPageName,
            Page_URL__c                           = input.pageUrl,
            Referrer_URL__c                       = input.referrerUrl,
            Event_Type__c                         = resolvedEventType,
            Search_Term__c                        = input.searchTerm,
            Knowledge__c                          = knowledgeId,
            Knowledge_Article_Version_Number__c   = knowledgeVersionNum,
            Device_Type__c                        = input.deviceType,
            Screen__c                             = input.screen,
            Browser__c                            = input.browser,
            OS__c                                 = input.os,
            User_ID__c                            = input.userId,
            Environment__c                        = resolveEnvironment(),
            Logged_In_As_User_Session__c          = input.isInternal == true,
            Viewport__c                           = input.viewport,
            Language__c                           = input.language,
            Time_Zone__c                          = input.timeZone
        );

        Database.SaveResult result = Database.insert(event, false, AccessLevel.SYSTEM_MODE);

        if (!result.isSuccess()) {
            List<String> messages = new List<String>();
            for (Database.Error err : result.getErrors()) {
                messages.add(err.getMessage());
            }
            throw new AuraHandledException('Portal_Analytics__c insert failed: ' + String.join(messages, ', '));
        }

        return result.getId();
    }
}