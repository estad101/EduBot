# Database Settings - Visual Flow Diagram

## Application Startup Flow

```
┌─────────────────────────────────────────────────────────────┐
│         Application Start (main.py)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ init_db()             │
         │ Initialize Database   │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────────────────┐
         │ init_settings_from_db(db)         │
         │ Initialize Settings Service       │
         └───────────┬───────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    ┌──────────────┐   ┌──────────────────┐
    │ Load from DB │   │ Database Empty?  │
    │ successful   │   └────────┬─────────┘
    │              │            │
    │              │      ┌─────┴──────┐
    │              │      │            │
    │              │      ▼            ▼
    │              │  Seed from    Skip seeding
    │              │  env vars        (use env)
    └──────┬───────┘      │            │
           │              └─────┬──────┘
           │                    │
           ▼                    ▼
    ┌──────────────────────────────────┐
    │ Load All Settings into Cache     │
    │ _settings_cache = {...}          │
    └──────────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────┐
    │ ✓ Ready to handle requests       │
    │ Credentials cached in memory     │
    └──────────────────────────────────┘
```

## WhatsApp Message Sending Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Incoming WhatsApp Message / Send WhatsApp Response         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
     ┌───────────────────────────────────┐
     │ WhatsAppService.send_message()    │
     │ or send_interactive_buttons()     │
     └────────────┬──────────────────────┘
                  │
                  ▼
     ┌────────────────────────────────────┐
     │ get_api_credentials()              │
     │ - Get token & phone_number_id      │
     └────────────┬─────────────────────┘
                  │
          ┌───────┴───────┐
          │               │
          ▼               ▼
    ┌──────────┐  ┌──────────────────┐
    │Memory    │  │Memory Cache      │
    │Cache Hit?│  │HIT? ✓ INSTANT    │
    └──────────┘  └──────────────────┘
                  
    NO ↓
    ┌──────────────────────┐
    │ Try Environment Var  │
    │ (fallback)           │
    └──────────┬───────────┘
               │
    NO ↓       │ YES ↓
    │      ┌───────────────┐
    │      │ Return & Cache│
    │      └───────────────┘
    │
    ▼
    ┌──────────────────────┐
    │ Query Database (rare)│
    │ If db session given  │
    └──────────┬───────────┘
               │
               ▼
    ┌───────────────────┐
    │ Return & Update   │
    │ Memory Cache      │
    └───────┬───────────┘
            │
            ▼
    ┌───────────────────────────────────┐
    │ Use Credentials for API Call      │
    │ POST to graph.facebook.com/v22.0  │
    └───────────────────────────────────┘
            │
            ▼
    ┌───────────────────────────────────┐
    │ Send WhatsApp Message Successfully│
    └───────────────────────────────────┘
```

## Settings Update Flow

```
┌─────────────────────────────────────────────────────────────┐
│  User Updates Settings at /settings                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────┐
    │ Admin Panel Form                   │
    │ - Token field                      │
    │ - Phone ID field                   │
    │ - Business ID field                │
    │ - Phone Number field               │
    │ [SAVE SETTINGS BUTTON]             │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ POST /api/admin/settings/update    │
    │ {whatsapp_api_key: "...",          │
    │  whatsapp_phone_number_id: "...",  │
    │  ...}                              │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ API Endpoint (admin/routes/api.py) │
    │ @router.post("/settings/update")   │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ For each setting:                  │
    │ - Query database for setting       │
    │ - Update value or create new       │
    │ - Add to session                   │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ db.commit()                        │
    │ Settings saved to database         │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ refresh_cache(db)                  │
    │ from services.settings_service     │
    └────────────┬───────────────────────┘
                 │
    ┌────────────┴───────────┐
    │                        │
    ▼                        ▼
┌──────────────┐    ┌──────────────────┐
│Clear Memory  │    │Load ALL Settings │
│Cache Dict    │    │FROM DATABASE      │
└──────────────┘    └──────────────────┘
    │                        │
    └────────────┬───────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ _settings_cache = {                │
    │   "whatsapp_api_key": "new_token", │
    │   "whatsapp_phone_number_id": ..., │
    │   ...                              │
    │ }                                  │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ Return Success Response            │
    │ {status: "success",                │
    │  message: "Settings updated..."}   │
    └────────────┬───────────────────────┘
                 │
                 ▼
    ┌────────────────────────────────────┐
    │ Admin Panel Shows Success          │
    │ "Settings saved successfully"      │
    │ ✓ New values take effect INSTANTLY │
    └────────────────────────────────────┘
```

## Settings Lookup Hierarchy

```
REQUEST: get_setting("whatsapp_api_key")
         │
         ▼
    ┌─────────────────────────────────┐
    │ Check Memory Cache              │
    │ "whatsapp_api_key" in           │
    │ _settings_cache?                │
    └─────────┬───────────────────────┘
              │
         YES  │  NO
             │  │
             │  ▼
             │  ┌──────────────────────────┐
             │  │ Check Environment Var    │
             │  │ getattr(settings, key)   │
             │  └──────────┬───────────────┘
             │             │
             │        YES  │  NO
             │            │  │
             │            │  ▼
             │            │  ┌────────────────────────┐
             │            │  │ Query Database         │
             │            │  │ (if db session given)  │
             │            │  └────────────┬───────────┘
             │            │               │
             │            │          YES  │  NO
             │            │              │  │
             │            │              │  ▼
             │            │              │  Return Default
             │            │              │  (None)
             │            │              │
    ┌────────┴────────────┴──────────────┴──┐
    │                                      │
    ▼                                      ▼
RETURN VALUE & UPDATE CACHE
(If not already cached)
```

## Database Schema

```
┌──────────────────────────────────────────┐
│         admin_settings TABLE             │
├────────┬──────────┬────────┬─────────────┤
│ id (PK)│ key (UK) │ value  │description  │
├────────┼──────────┼────────┼─────────────┤
│ 1      │ whatsapp │ EAAC.. │ WhatsApp    │
│        │ _api_key │ (token)│ API Token   │
├────────┼──────────┼────────┼─────────────┤
│ 2      │ whatsapp │ 79746..│ WhatsApp    │
│        │ _phone   │        │ Phone ID    │
│        │ _number  │        │             │
│        │ _id      │        │             │
├────────┼──────────┼────────┼─────────────┤
│ 3      │ whatsapp │ 10723..│ WhatsApp    │
│        │ _busines │        │ Business    │
│        │ s_       │        │ Account ID  │
│        │ account  │        │             │
│        │ _id      │        │             │
├────────┼──────────┼────────┼─────────────┤
│ 4      │ whatsapp │ +2348..│ WhatsApp    │
│        │ _phone   │        │ Phone No.   │
│        │ _number  │        │             │
├────────┼──────────┼────────┼─────────────┤
│ ...    │ ...      │ ...    │ ...         │
└────────┴──────────┴────────┴─────────────┘

Fields:
- id: Auto-increment primary key
- key: Unique setting name
- value: Setting value (text)
- description: Human-readable description
- created_at: Timestamp (auto)
- updated_at: Timestamp (auto on update)
```

## Caching Strategy

```
STARTUP
   │
   ▼
┌──────────────────────────────┐
│ _settings_cache = {}         │
│ _cache_initialized = False   │
└──────────────┬───────────────┘
               │
               ▼
      ┌────────────────────┐
      │ Load from Database │
      └────────────┬───────┘
                   │
                   ▼
      ┌────────────────────────────────┐
      │ _settings_cache = {            │
      │   "whatsapp_api_key": "token", │
      │   "paystack_public_key": "pk",│
      │   ... (all from DB)            │
      │ }                              │
      │ _cache_initialized = True      │
      └────────────┬───────────────────┘
                   │
RUNTIME REQUEST: get_setting("whatsapp_api_key")
   │
   ▼
 ┌─────────────────────────────────┐
 │ Is "whatsapp_api_key"           │
 │ in _settings_cache?             │
 └─────────┬───────────────────────┘
           │
      YES  │  Immediate return (< 1ms)
           │
           ▼
      ┌─────────────────┐
      │ "EAAck..." ◄────┤─ Cached value
      └─────────────────┘

AFTER UPDATE: refresh_cache(db)
   │
   ▼
┌──────────────────────────────┐
│ _settings_cache.clear()      │
│ _settings_cache = {}         │
└──────────────┬───────────────┘
               │
               ▼
      ┌────────────────────┐
      │ Reload from DB     │
      │ (all rows)         │
      └────────────┬───────┘
               │
               ▼
      ┌──────────────────────────────┐
      │ _settings_cache = {          │
      │   "whatsapp_api_key": "new", │  ◄─ Updated
      │   ...                        │
      │ }                            │
      └──────────────────────────────┘
```

## Sequence: Complete User Journey

```
TIME    USER                    ADMIN UI              API BACKEND              DATABASE
────    ────                    ────────              ───────────              ────────
│
t0      Click Settings          │                     │                        │
        Page                    │                     │                        │
│       │                                             │                        │
└──────►├─────────────────────► GET /settings ──────► │                        │
        │                                             │                        │
        │                                             └───────────────────────►│
        │                                                                       │Query
        │                                                                       │settings
        │                                             ◄───────────────────────┤
        │                                             │{whatsapp_api_key: ...} │
        │                       ◄─────────────────────┤                        │
        │Display current values │                     │                        │
        │                       │                     │                        │
t1      User updates            │                     │                        │
        token field             │                     │                        │
        │                       │                     │                        │
        │Clicks SAVE            │                     │                        │
t2      │                       │                     │                        │
        ├──────────────────────►│ POST /settings/update                        │
        │                       ├────────────────────►│                        │
        │                       │                     │                        │
        │                       │                     └───────────────────────►│
        │                       │                                              │UPDATE
        │                       │                                              │whatsapp_
        │                       │                                              │api_key
        │                       │                                              │
        │                       │                     ◄───────────────────────┤
        │                       │                     │ UPDATE successful      │
        │                       │                     │                        │
        │                       │                     ├─ refresh_cache()       │
        │                       │                     │  _settings_cache =     │
        │                       │                     │  {new values}          │
        │                       │                     │                        │
        │                       │◄─────────────────────                        │
        │                       │ {status: success}                            │
        │                       │                                              │
        │   ◄───────────────────┤                                              │
t3      │ Success message       │                                              │
        │ NEW CREDENTIALS LIVE! │                                              │
        │                       │                                              │
        ├─ Send Test WhatsApp   │                                              │
        │ Message              │                                              │
        │    │                                                                 │
        │    └──────────────────────────────────────►│                        │
        │                                             │ WhatsAppService        │
        │                                             │ .send_message()        │
        │                                             │                        │
        │                                             ├─ get_api_credentials()│
        │                                             │  (from cache, instant)│
        │                                             │                        │
        │                                             ├─ POST to facebook.com │
        │                                             │  /v22.0/send          │
        │                                             │  (using NEW token)    │
        │                                             │                        │
        │                       ◄─────────────────────                        │
        │                       │ Message sent OK!   │                        │
        │                       │                    │                        │
t4      │ ◄──────────────────────                    │                        │
        │ Test message success! │                    │                        │
        │                       │                    │                        │
        │ ✓ All done!          │                    │                        │
        │                       │                    │                        │
```

