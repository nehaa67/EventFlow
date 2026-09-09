--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2026-09-07 21:08:29

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2 (class 3079 OID 24925)
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- TOC entry 5968 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 223 (class 1259 OID 24713)
-- Name: access_points; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.access_points (
    access_point_id integer NOT NULL,
    venue_id integer NOT NULL,
    zone_id integer,
    access_name character varying(100) NOT NULL,
    access_type character varying(30),
    latitude double precision,
    longitude double precision,
    location public.geography(Point,4326),
    name character varying(255),
    capacity_per_minute integer,
    status character varying(50),
    data_status character varying(30)
);


ALTER TABLE public.access_points OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 24712)
-- Name: access_points_access_point_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.access_points_access_point_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.access_points_access_point_id_seq OWNER TO postgres;

--
-- TOC entry 5969 (class 0 OID 0)
-- Dependencies: 222
-- Name: access_points_access_point_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.access_points_access_point_id_seq OWNED BY public.access_points.access_point_id;


--
-- TOC entry 229 (class 1259 OID 24754)
-- Name: accommodation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accommodation (
    accommodation_id integer NOT NULL,
    name character varying(150) NOT NULL,
    accommodation_type character varying(50),
    latitude double precision,
    longitude double precision,
    capacity integer,
    location public.geography(Point,4326),
    data_source character varying(100),
    data_status character varying(30),
    available_units integer,
    occupancy_percentage numeric(5,2),
    status character varying(50)
);


ALTER TABLE public.accommodation OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 24753)
-- Name: accommodation_accommodation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.accommodation_accommodation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.accommodation_accommodation_id_seq OWNER TO postgres;

--
-- TOC entry 5970 (class 0 OID 0)
-- Dependencies: 228
-- Name: accommodation_accommodation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.accommodation_accommodation_id_seq OWNED BY public.accommodation.accommodation_id;


--
-- TOC entry 249 (class 1259 OID 24891)
-- Name: applied_actions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.applied_actions (
    action_id integer NOT NULL,
    event_id integer NOT NULL,
    intervention_id integer NOT NULL,
    applied_at timestamp without time zone NOT NULL,
    approved_by character varying(150),
    action_status character varying(30) DEFAULT 'APPLIED'::character varying,
    action_details text,
    resulting_state_version integer
);


ALTER TABLE public.applied_actions OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 24890)
-- Name: applied_actions_action_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.applied_actions_action_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.applied_actions_action_id_seq OWNER TO postgres;

--
-- TOC entry 5971 (class 0 OID 0)
-- Dependencies: 248
-- Name: applied_actions_action_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.applied_actions_action_id_seq OWNED BY public.applied_actions.action_id;


--
-- TOC entry 251 (class 1259 OID 24911)
-- Name: attendee_guidance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendee_guidance (
    guidance_id integer NOT NULL,
    event_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    guidance_type character varying(100),
    message text NOT NULL,
    target_area character varying(150),
    priority character varying(30),
    status character varying(30) DEFAULT 'ACTIVE'::character varying,
    guidance_data jsonb,
    target_zone_id integer,
    target_access_point_id integer,
    target_route_id integer,
    valid_until timestamp without time zone
);


ALTER TABLE public.attendee_guidance OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 24910)
-- Name: attendee_guidance_guidance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendee_guidance_guidance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendee_guidance_guidance_id_seq OWNER TO postgres;

--
-- TOC entry 5972 (class 0 OID 0)
-- Dependencies: 250
-- Name: attendee_guidance_guidance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendee_guidance_guidance_id_seq OWNED BY public.attendee_guidance.guidance_id;


--
-- TOC entry 231 (class 1259 OID 24761)
-- Name: conditions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conditions (
    condition_id integer NOT NULL,
    event_id integer,
    recorded_at timestamp without time zone NOT NULL,
    weather_type character varying(50),
    temperature numeric(5,2),
    rainfall_mm numeric(6,2),
    visibility_km numeric(5,2),
    severity character varying(30),
    "timestamp" timestamp without time zone,
    data_status character varying(30)
);


ALTER TABLE public.conditions OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 24760)
-- Name: conditions_condition_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.conditions_condition_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.conditions_condition_id_seq OWNER TO postgres;

--
-- TOC entry 5973 (class 0 OID 0)
-- Dependencies: 230
-- Name: conditions_condition_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.conditions_condition_id_seq OWNED BY public.conditions.condition_id;


--
-- TOC entry 237 (class 1259 OID 24789)
-- Name: crowd_state; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.crowd_state (
    crowd_state_id integer NOT NULL,
    event_id integer NOT NULL,
    zone_id integer NOT NULL,
    recorded_at timestamp without time zone NOT NULL,
    current_count integer,
    inflow_rate numeric(8,2),
    outflow_rate numeric(8,2),
    density numeric(8,2),
    load_percentage numeric(6,2),
    "timestamp" timestamp without time zone,
    data_status character varying(30)
);


ALTER TABLE public.crowd_state OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 24788)
-- Name: crowd_state_crowd_state_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.crowd_state_crowd_state_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.crowd_state_crowd_state_id_seq OWNER TO postgres;

--
-- TOC entry 5974 (class 0 OID 0)
-- Dependencies: 236
-- Name: crowd_state_crowd_state_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.crowd_state_crowd_state_id_seq OWNED BY public.crowd_state.crowd_state_id;


--
-- TOC entry 239 (class 1259 OID 24806)
-- Name: event_state; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.event_state (
    event_state_id integer NOT NULL,
    event_id integer NOT NULL,
    recorded_at timestamp without time zone NOT NULL,
    scenario character varying(50),
    overall_status character varying(50),
    crowd_level character varying(30),
    transport_status character varying(30),
    weather_status character varying(30),
    active_incidents integer DEFAULT 0,
    risk_level character varying(30),
    state_id integer,
    "timestamp" timestamp without time zone,
    state_version integer DEFAULT 1,
    state_data jsonb,
    overall_risk_score numeric(5,2),
    overall_risk_level character varying(50),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.event_state OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 24805)
-- Name: event_state_event_state_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.event_state_event_state_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_state_event_state_id_seq OWNER TO postgres;

--
-- TOC entry 5975 (class 0 OID 0)
-- Dependencies: 238
-- Name: event_state_event_state_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.event_state_event_state_id_seq OWNED BY public.event_state.event_state_id;


--
-- TOC entry 235 (class 1259 OID 24777)
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events (
    event_id integer NOT NULL,
    venue_id integer NOT NULL,
    event_name character varying(200) NOT NULL,
    event_type character varying(100),
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    expected_attendance integer,
    name character varying(255),
    status character varying(50),
    scenario character varying(100),
    data_status character varying(30),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.events OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 24776)
-- Name: events_event_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.events_event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.events_event_id_seq OWNER TO postgres;

--
-- TOC entry 5976 (class 0 OID 0)
-- Dependencies: 234
-- Name: events_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.events_event_id_seq OWNED BY public.events.event_id;


--
-- TOC entry 233 (class 1259 OID 24768)
-- Name: incidents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.incidents (
    incident_id integer NOT NULL,
    event_id integer,
    incident_type character varying(100) NOT NULL,
    description text,
    severity character varying(30),
    started_at timestamp without time zone,
    ended_at timestamp without time zone,
    entity_type character varying(50),
    entity_id integer,
    location public.geography(Point,4326),
    status character varying(50),
    reported_at timestamp without time zone
);


ALTER TABLE public.incidents OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 24767)
-- Name: incidents_incident_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.incidents_incident_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.incidents_incident_id_seq OWNER TO postgres;

--
-- TOC entry 5977 (class 0 OID 0)
-- Dependencies: 232
-- Name: incidents_incident_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.incidents_incident_id_seq OWNED BY public.incidents.incident_id;


--
-- TOC entry 245 (class 1259 OID 24856)
-- Name: interventions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interventions (
    intervention_id integer NOT NULL,
    event_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    intervention_name character varying(150) NOT NULL,
    intervention_type character varying(100),
    description text,
    target_area character varying(150),
    priority character varying(30),
    status character varying(30) DEFAULT 'PROPOSED'::character varying,
    parameters jsonb,
    expected_risk_reduction numeric(5,2),
    expected_capacity_change numeric(5,2),
    people_benefited integer,
    time_saved_minutes integer,
    feasibility_score numeric(5,2),
    cost_score numeric(5,2),
    operational_impact numeric(5,2),
    overall_score numeric(5,2),
    rank integer
);


ALTER TABLE public.interventions OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 24855)
-- Name: interventions_intervention_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interventions_intervention_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interventions_intervention_id_seq OWNER TO postgres;

--
-- TOC entry 5978 (class 0 OID 0)
-- Dependencies: 244
-- Name: interventions_intervention_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interventions_intervention_id_seq OWNED BY public.interventions.intervention_id;


--
-- TOC entry 241 (class 1259 OID 24819)
-- Name: predictions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.predictions (
    prediction_id integer NOT NULL,
    event_id integer NOT NULL,
    zone_id integer,
    created_at timestamp without time zone NOT NULL,
    prediction_type character varying(100),
    predicted_value numeric(10,2),
    prediction_unit character varying(50),
    confidence_score numeric(5,2),
    prediction_horizon_minutes integer,
    target_time timestamp without time zone,
    predicted_count integer,
    predicted_load_percentage numeric(5,2),
    breach_eta_minutes integer,
    model_name character varying(100),
    model_version character varying(50),
    confidence numeric(5,2)
);


ALTER TABLE public.predictions OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 24818)
-- Name: predictions_prediction_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.predictions_prediction_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.predictions_prediction_id_seq OWNER TO postgres;

--
-- TOC entry 5979 (class 0 OID 0)
-- Dependencies: 240
-- Name: predictions_prediction_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.predictions_prediction_id_seq OWNED BY public.predictions.prediction_id;


--
-- TOC entry 243 (class 1259 OID 24836)
-- Name: risk_assessments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.risk_assessments (
    risk_id integer NOT NULL,
    event_id integer NOT NULL,
    zone_id integer,
    assessed_at timestamp without time zone NOT NULL,
    risk_type character varying(100),
    risk_score numeric(5,2),
    risk_level character varying(30),
    hotspot boolean DEFAULT false,
    explanation text,
    entity_type character varying(50),
    entity_id integer,
    component_scores jsonb,
    reason_signals jsonb
);


ALTER TABLE public.risk_assessments OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 24835)
-- Name: risk_assessments_risk_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.risk_assessments_risk_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.risk_assessments_risk_id_seq OWNER TO postgres;

--
-- TOC entry 5980 (class 0 OID 0)
-- Dependencies: 242
-- Name: risk_assessments_risk_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.risk_assessments_risk_id_seq OWNED BY public.risk_assessments.risk_id;


--
-- TOC entry 227 (class 1259 OID 24737)
-- Name: routes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.routes (
    route_id integer NOT NULL,
    route_name character varying(150) NOT NULL,
    route_type character varying(50),
    from_node_id integer,
    to_node_id integer,
    distance_km double precision,
    estimated_time_minutes integer,
    route_geometry public.geography(LineString,4326),
    name character varying(255),
    capacity integer DEFAULT 0,
    current_load integer DEFAULT 0,
    travel_time_minutes numeric,
    geometry public.geometry(LineString,4326),
    status character varying(50),
    data_status character varying(30)
);


ALTER TABLE public.routes OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 24736)
-- Name: routes_route_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.routes_route_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.routes_route_id_seq OWNER TO postgres;

--
-- TOC entry 5981 (class 0 OID 0)
-- Dependencies: 226
-- Name: routes_route_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.routes_route_id_seq OWNED BY public.routes.route_id;


--
-- TOC entry 247 (class 1259 OID 24872)
-- Name: simulations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.simulations (
    simulation_id integer NOT NULL,
    event_id integer NOT NULL,
    intervention_id integer,
    created_at timestamp without time zone NOT NULL,
    simulation_name character varying(150),
    simulated_crowd_load numeric(6,2),
    simulated_transport_load numeric(6,2),
    simulated_risk_score numeric(5,2),
    outcome character varying(50),
    result_summary text,
    simulation_data jsonb,
    before_state jsonb,
    after_state jsonb,
    affected_nodes jsonb,
    side_effects jsonb,
    feasible boolean,
    simulation_score numeric(5,2)
);


ALTER TABLE public.simulations OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 24871)
-- Name: simulations_simulation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.simulations_simulation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.simulations_simulation_id_seq OWNER TO postgres;

--
-- TOC entry 5982 (class 0 OID 0)
-- Dependencies: 246
-- Name: simulations_simulation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.simulations_simulation_id_seq OWNED BY public.simulations.simulation_id;


--
-- TOC entry 225 (class 1259 OID 24730)
-- Name: transport_nodes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transport_nodes (
    transport_node_id integer NOT NULL,
    node_name character varying(150) NOT NULL,
    node_type character varying(50),
    latitude double precision,
    longitude double precision,
    capacity integer,
    location public.geography(Point,4326),
    current_load integer DEFAULT 0,
    load_percentage numeric(5,2) DEFAULT 0,
    status character varying(50),
    data_status character varying(30)
);


ALTER TABLE public.transport_nodes OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 24729)
-- Name: transport_nodes_transport_node_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transport_nodes_transport_node_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.transport_nodes_transport_node_id_seq OWNER TO postgres;

--
-- TOC entry 5983 (class 0 OID 0)
-- Dependencies: 224
-- Name: transport_nodes_transport_node_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transport_nodes_transport_node_id_seq OWNED BY public.transport_nodes.transport_node_id;


--
-- TOC entry 219 (class 1259 OID 24692)
-- Name: venues; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.venues (
    venue_id integer NOT NULL,
    venue_name character varying(150) NOT NULL,
    address text,
    capacity integer,
    latitude double precision,
    longitude double precision,
    location public.geography(Point,4326),
    name character varying(255),
    venue_type character varying(100),
    status character varying(50),
    data_status character varying(30),
    source character varying(255)
);


ALTER TABLE public.venues OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 24691)
-- Name: venues_venue_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.venues_venue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.venues_venue_id_seq OWNER TO postgres;

--
-- TOC entry 5984 (class 0 OID 0)
-- Dependencies: 218
-- Name: venues_venue_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.venues_venue_id_seq OWNED BY public.venues.venue_id;


--
-- TOC entry 221 (class 1259 OID 24701)
-- Name: zones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.zones (
    zone_id integer NOT NULL,
    venue_id integer NOT NULL,
    zone_name character varying(150) NOT NULL,
    capacity integer,
    zone_type character varying(50),
    boundary public.geography(Polygon,4326),
    name character varying(255),
    parent_zone_id integer,
    status character varying(50),
    data_status character varying(30)
);


ALTER TABLE public.zones OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 24700)
-- Name: zones_zone_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zones_zone_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.zones_zone_id_seq OWNER TO postgres;

--
-- TOC entry 5985 (class 0 OID 0)
-- Dependencies: 220
-- Name: zones_zone_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zones_zone_id_seq OWNED BY public.zones.zone_id;


--
-- TOC entry 5689 (class 2604 OID 24716)
-- Name: access_points access_point_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_points ALTER COLUMN access_point_id SET DEFAULT nextval('public.access_points_access_point_id_seq'::regclass);


--
-- TOC entry 5696 (class 2604 OID 24757)
-- Name: accommodation accommodation_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accommodation ALTER COLUMN accommodation_id SET DEFAULT nextval('public.accommodation_accommodation_id_seq'::regclass);


--
-- TOC entry 5712 (class 2604 OID 24894)
-- Name: applied_actions action_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applied_actions ALTER COLUMN action_id SET DEFAULT nextval('public.applied_actions_action_id_seq'::regclass);


--
-- TOC entry 5714 (class 2604 OID 24914)
-- Name: attendee_guidance guidance_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendee_guidance ALTER COLUMN guidance_id SET DEFAULT nextval('public.attendee_guidance_guidance_id_seq'::regclass);


--
-- TOC entry 5697 (class 2604 OID 24764)
-- Name: conditions condition_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conditions ALTER COLUMN condition_id SET DEFAULT nextval('public.conditions_condition_id_seq'::regclass);


--
-- TOC entry 5701 (class 2604 OID 24792)
-- Name: crowd_state crowd_state_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crowd_state ALTER COLUMN crowd_state_id SET DEFAULT nextval('public.crowd_state_crowd_state_id_seq'::regclass);


--
-- TOC entry 5702 (class 2604 OID 24809)
-- Name: event_state event_state_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_state ALTER COLUMN event_state_id SET DEFAULT nextval('public.event_state_event_state_id_seq'::regclass);


--
-- TOC entry 5699 (class 2604 OID 24780)
-- Name: events event_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events ALTER COLUMN event_id SET DEFAULT nextval('public.events_event_id_seq'::regclass);


--
-- TOC entry 5698 (class 2604 OID 24771)
-- Name: incidents incident_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents ALTER COLUMN incident_id SET DEFAULT nextval('public.incidents_incident_id_seq'::regclass);


--
-- TOC entry 5709 (class 2604 OID 24859)
-- Name: interventions intervention_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interventions ALTER COLUMN intervention_id SET DEFAULT nextval('public.interventions_intervention_id_seq'::regclass);


--
-- TOC entry 5706 (class 2604 OID 24822)
-- Name: predictions prediction_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.predictions ALTER COLUMN prediction_id SET DEFAULT nextval('public.predictions_prediction_id_seq'::regclass);


--
-- TOC entry 5707 (class 2604 OID 24839)
-- Name: risk_assessments risk_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_assessments ALTER COLUMN risk_id SET DEFAULT nextval('public.risk_assessments_risk_id_seq'::regclass);


--
-- TOC entry 5693 (class 2604 OID 24740)
-- Name: routes route_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes ALTER COLUMN route_id SET DEFAULT nextval('public.routes_route_id_seq'::regclass);


--
-- TOC entry 5711 (class 2604 OID 24875)
-- Name: simulations simulation_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulations ALTER COLUMN simulation_id SET DEFAULT nextval('public.simulations_simulation_id_seq'::regclass);


--
-- TOC entry 5690 (class 2604 OID 24733)
-- Name: transport_nodes transport_node_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transport_nodes ALTER COLUMN transport_node_id SET DEFAULT nextval('public.transport_nodes_transport_node_id_seq'::regclass);


--
-- TOC entry 5687 (class 2604 OID 24695)
-- Name: venues venue_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venues ALTER COLUMN venue_id SET DEFAULT nextval('public.venues_venue_id_seq'::regclass);


--
-- TOC entry 5688 (class 2604 OID 24704)
-- Name: zones zone_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones ALTER COLUMN zone_id SET DEFAULT nextval('public.zones_zone_id_seq'::regclass);


--
-- TOC entry 5934 (class 0 OID 24713)
-- Dependencies: 223
-- Data for Name: access_points; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.access_points (access_point_id, venue_id, zone_id, access_name, access_type, latitude, longitude, location, name, capacity_per_minute, status, data_status) FROM stdin;
1	1	1	Gate 1	ENTRY_EXIT	18.9392	72.8253	0101000020E6100000E25817B7D1345240386744696FF03240	Gate 1	\N	ACTIVE	VALIDATED
2	1	2	Gate 2	ENTRY_EXIT	18.939	72.8254	0101000020E61000009487855AD3345240AAF1D24D62F03240	Gate 2	\N	ACTIVE	VALIDATED
3	1	3	Gate 3	ENTRY_EXIT	18.9387	72.8253	0101000020E6100000E25817B7D134524055C1A8A44EF03240	Gate 3	\N	ACTIVE	VALIDATED
4	1	4	Gate 4	ENTRY_EXIT	18.9385	72.8256	0101000020E6100000F7E461A1D6345240C74B378941F03240	Gate 4	\N	ACTIVE	VALIDATED
5	1	5	Gate 5	ENTRY_EXIT	18.9384	72.8259	0101000020E61000000D71AC8BDB34524000917EFB3AF03240	Gate 5	\N	ACTIVE	VALIDATED
6	1	6	Gate 6	ENTRY_EXIT	18.9387	72.8261	0101000020E610000070CE88D2DE34524055C1A8A44EF03240	Gate 6	\N	ACTIVE	VALIDATED
7	1	7	Gate 7	ENTRY_EXIT	18.939	72.826	0101000020E6100000BE9F1A2FDD345240AAF1D24D62F03240	Gate 7	\N	ACTIVE	VALIDATED
\.


--
-- TOC entry 5940 (class 0 OID 24754)
-- Dependencies: 229
-- Data for Name: accommodation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.accommodation (accommodation_id, name, accommodation_type, latitude, longitude, capacity, location, data_source, data_status, available_units, occupancy_percentage, status) FROM stdin;
1	Churchgate Hotel Zone	HOTEL_ZONE	18.9345	72.8265	3000	0101000020E610000037894160E5345240AC1C5A643BEF3240	Demo / Geographic Seed Data	DEMO	1350	55.00	OPEN
2	Marine Drive Hotel Zone	HOTEL_ZONE	18.943	72.823	2500	0101000020E6100000E9263108AC345240C520B07268F13240	Demo / Geographic Seed Data	DEMO	1000	60.00	OPEN
3	Colaba Hotel Zone	HOTEL_ZONE	18.922	72.834	5000	0101000020E61000004C3789416035524079E9263108EC3240	Demo / Geographic Seed Data	DEMO	1500	70.00	OPEN
\.


--
-- TOC entry 5960 (class 0 OID 24891)
-- Dependencies: 249
-- Data for Name: applied_actions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.applied_actions (action_id, event_id, intervention_id, applied_at, approved_by, action_status, action_details, resulting_state_version) FROM stdin;
1	1	2	2026-09-06 21:50:00	Event Organizer	APPLIED	Additional shuttle service activated.	\N
\.


--
-- TOC entry 5962 (class 0 OID 24911)
-- Dependencies: 251
-- Data for Name: attendee_guidance; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.attendee_guidance (guidance_id, event_id, created_at, guidance_type, message, target_area, priority, status, guidance_data, target_zone_id, target_access_point_id, target_route_id, valid_until) FROM stdin;
2	1	2026-09-06 21:51:00	TRANSPORT	Use additional shuttle services and avoid congested exits.	Wankhede Stadium	HIGH	ACTIVE	\N	\N	\N	\N	\N
\.


--
-- TOC entry 5942 (class 0 OID 24761)
-- Dependencies: 231
-- Data for Name: conditions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.conditions (condition_id, event_id, recorded_at, weather_type, temperature, rainfall_mm, visibility_km, severity, "timestamp", data_status) FROM stdin;
1	1	2026-09-06 21:30:00	HEAVY_RAIN	27.50	18.00	2.50	HIGH	2026-09-06 21:30:00	VALIDATED
2	1	2026-09-06 18:00:00	CLEAR	29.00	0.00	10.00	LOW	2026-09-06 18:00:00	VALIDATED
3	1	2026-09-06 19:00:00	CLOUDY	28.50	0.00	9.00	LOW	2026-09-06 19:00:00	VALIDATED
4	1	2026-09-06 20:00:00	CLOUDY	28.00	2.00	8.00	MEDIUM	2026-09-06 20:00:00	VALIDATED
5	1	2026-09-06 20:30:00	LIGHT_RAIN	27.80	5.00	6.00	MEDIUM	2026-09-06 20:30:00	VALIDATED
6	1	2026-09-06 21:00:00	MODERATE_RAIN	27.60	10.00	4.00	HIGH	2026-09-06 21:00:00	VALIDATED
7	1	2026-09-06 21:15:00	HEAVY_RAIN	27.50	15.00	3.00	HIGH	2026-09-06 21:15:00	VALIDATED
8	1	2026-09-06 21:45:00	HEAVY_RAIN	27.30	20.00	2.00	CRITICAL	2026-09-06 21:45:00	VALIDATED
\.


--
-- TOC entry 5948 (class 0 OID 24789)
-- Dependencies: 237
-- Data for Name: crowd_state; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.crowd_state (crowd_state_id, event_id, zone_id, recorded_at, current_count, inflow_rate, outflow_rate, density, load_percentage, "timestamp", data_status) FROM stdin;
72	1	1	2026-09-06 20:05:00	1900	80.00	50.00	47.33	47.50	2026-09-06 20:05:00	SIMULATED
73	1	1	2026-09-06 20:10:00	2000	80.00	50.00	49.67	50.00	2026-09-06 20:10:00	SIMULATED
74	1	2	2026-09-06 20:05:00	1783	75.00	48.00	45.67	44.58	2026-09-06 20:05:00	SIMULATED
75	1	2	2026-09-06 20:10:00	1867	75.00	48.00	47.33	46.67	2026-09-06 20:10:00	SIMULATED
76	1	3	2026-09-06 20:05:00	1683	70.00	45.00	43.00	48.09	2026-09-06 20:05:00	SIMULATED
77	1	3	2026-09-06 20:10:00	1767	70.00	45.00	45.00	50.48	2026-09-06 20:10:00	SIMULATED
78	1	4	2026-09-06 20:05:00	2000	85.00	50.00	50.33	50.00	2026-09-06 20:05:00	SIMULATED
79	1	4	2026-09-06 20:10:00	2100	85.00	50.00	52.67	52.50	2026-09-06 20:10:00	SIMULATED
80	1	5	2026-09-06 20:05:00	1367	60.00	40.00	37.33	39.05	2026-09-06 20:05:00	SIMULATED
81	1	5	2026-09-06 20:10:00	1433	60.00	40.00	38.67	40.95	2026-09-06 20:10:00	SIMULATED
82	1	6	2026-09-06 20:05:00	1267	55.00	38.00	36.00	42.22	2026-09-06 20:05:00	SIMULATED
83	1	6	2026-09-06 20:10:00	1333	55.00	38.00	37.00	44.45	2026-09-06 20:10:00	SIMULATED
84	1	7	2026-09-06 20:05:00	2100	90.00	45.00	52.67	52.50	2026-09-06 20:05:00	SIMULATED
85	1	7	2026-09-06 20:10:00	2200	90.00	45.00	55.33	55.00	2026-09-06 20:10:00	SIMULATED
86	1	8	2026-09-06 20:05:00	3667	120.00	60.00	54.33	51.65	2026-09-06 20:05:00	SIMULATED
87	1	8	2026-09-06 20:10:00	3833	120.00	60.00	56.67	53.99	2026-09-06 20:10:00	SIMULATED
88	1	1	2026-09-06 20:20:00	2200	90.00	55.00	54.67	55.00	2026-09-06 20:20:00	SIMULATED
89	1	1	2026-09-06 20:25:00	2300	90.00	55.00	57.33	57.50	2026-09-06 20:25:00	SIMULATED
90	1	2	2026-09-06 20:20:00	2033	85.00	50.00	51.00	50.83	2026-09-06 20:20:00	SIMULATED
91	1	2	2026-09-06 20:25:00	2117	85.00	50.00	53.00	52.92	2026-09-06 20:25:00	SIMULATED
92	1	3	2026-09-06 20:20:00	1933	80.00	48.00	49.33	55.24	2026-09-06 20:20:00	SIMULATED
93	1	3	2026-09-06 20:25:00	2017	80.00	48.00	51.67	57.62	2026-09-06 20:25:00	SIMULATED
94	1	4	2026-09-06 20:20:00	2300	95.00	55.00	57.67	57.50	2026-09-06 20:20:00	SIMULATED
95	1	4	2026-09-06 20:25:00	2400	95.00	55.00	60.33	60.00	2026-09-06 20:25:00	SIMULATED
96	1	5	2026-09-06 20:20:00	1583	65.00	42.00	42.00	45.24	2026-09-06 20:20:00	SIMULATED
97	1	5	2026-09-06 20:25:00	1667	65.00	42.00	44.00	47.62	2026-09-06 20:25:00	SIMULATED
98	1	6	2026-09-06 20:20:00	1467	60.00	40.00	40.00	48.89	2026-09-06 20:20:00	SIMULATED
99	1	6	2026-09-06 20:25:00	1533	60.00	40.00	42.00	51.11	2026-09-06 20:25:00	SIMULATED
100	1	7	2026-09-06 20:20:00	2433	100.00	48.00	61.33	60.83	2026-09-06 20:20:00	SIMULATED
101	1	7	2026-09-06 20:25:00	2567	100.00	48.00	64.67	64.17	2026-09-06 20:25:00	SIMULATED
102	1	8	2026-09-06 20:20:00	4167	140.00	65.00	61.67	58.69	2026-09-06 20:20:00	SIMULATED
103	1	8	2026-09-06 20:25:00	4333	140.00	65.00	64.33	61.03	2026-09-06 20:25:00	SIMULATED
104	1	1	2026-09-06 20:35:00	2500	100.00	60.00	62.67	62.50	2026-09-06 20:35:00	SIMULATED
105	1	1	2026-09-06 20:40:00	2600	100.00	60.00	65.33	65.00	2026-09-06 20:40:00	SIMULATED
106	1	2	2026-09-06 20:35:00	2283	90.00	55.00	57.00	57.08	2026-09-06 20:35:00	SIMULATED
107	1	2	2026-09-06 20:40:00	2367	90.00	55.00	59.00	59.17	2026-09-06 20:40:00	SIMULATED
108	1	3	2026-09-06 20:35:00	2183	85.00	50.00	56.00	62.38	2026-09-06 20:35:00	SIMULATED
109	1	3	2026-09-06 20:40:00	2267	85.00	50.00	58.00	64.76	2026-09-06 20:40:00	SIMULATED
110	1	4	2026-09-06 20:35:00	2600	110.00	60.00	65.33	65.00	2026-09-06 20:35:00	SIMULATED
111	1	4	2026-09-06 20:40:00	2700	110.00	60.00	67.67	67.50	2026-09-06 20:40:00	SIMULATED
112	1	5	2026-09-06 20:35:00	1817	70.00	45.00	48.00	51.90	2026-09-06 20:35:00	SIMULATED
113	1	5	2026-09-06 20:40:00	1883	70.00	45.00	50.00	53.81	2026-09-06 20:40:00	SIMULATED
114	1	6	2026-09-06 20:35:00	1667	65.00	42.00	45.33	55.55	2026-09-06 20:35:00	SIMULATED
115	1	6	2026-09-06 20:40:00	1733	65.00	42.00	46.67	57.78	2026-09-06 20:40:00	SIMULATED
116	1	7	2026-09-06 20:35:00	2833	115.00	50.00	71.33	70.83	2026-09-06 20:35:00	SIMULATED
117	1	7	2026-09-06 20:40:00	2967	115.00	50.00	74.67	74.17	2026-09-06 20:40:00	SIMULATED
118	1	8	2026-09-06 20:35:00	4667	155.00	70.00	69.33	65.73	2026-09-06 20:35:00	SIMULATED
119	1	8	2026-09-06 20:40:00	4833	155.00	70.00	71.67	68.07	2026-09-06 20:40:00	SIMULATED
120	1	1	2026-09-06 20:50:00	2799	110.00	65.00	70.49	69.98	2026-09-06 20:50:00	SIMULATED
121	1	1	2026-09-06 20:55:00	2898	110.00	65.00	72.99	72.45	2026-09-06 20:55:00	SIMULATED
122	1	1	2026-09-06 21:05:00	3078	122.10	72.15	77.52	76.95	2026-09-06 21:05:00	SIMULATED
123	1	1	2026-09-06 21:10:00	3159	122.10	72.15	79.56	78.98	2026-09-06 21:10:00	SIMULATED
124	1	1	2026-09-06 21:20:00	3294	132.00	78.00	82.96	82.35	2026-09-06 21:20:00	SIMULATED
125	1	1	2026-09-06 21:25:00	3348	132.00	78.00	84.32	83.70	2026-09-06 21:25:00	SIMULATED
126	1	1	2026-09-06 21:35:00	3501	138.60	81.90	87.84	87.53	2026-09-06 21:35:00	SIMULATED
127	1	2	2026-09-06 20:50:00	2540	95.00	60.00	63.24	63.50	2026-09-06 20:50:00	SIMULATED
128	1	2	2026-09-06 20:55:00	2630	95.00	60.00	65.47	65.74	2026-09-06 20:55:00	SIMULATED
129	1	2	2026-09-06 21:05:00	2793	105.45	66.60	69.54	69.83	2026-09-06 21:05:00	SIMULATED
1	1	1	2026-09-06 21:40:00	3600	120.00	80.00	90.00	90.00	2026-09-06 21:40:00	VALIDATED
2	1	2	2026-09-06 21:40:00	3200	100.00	70.00	82.00	80.00	2026-09-06 21:40:00	VALIDATED
3	1	3	2026-09-06 21:40:00	3100	90.00	60.00	79.00	88.57	2026-09-06 21:40:00	VALIDATED
4	1	4	2026-09-06 21:40:00	3800	140.00	65.00	95.00	95.00	2026-09-06 21:40:00	VALIDATED
5	1	5	2026-09-06 21:40:00	2500	80.00	50.00	70.00	71.43	2026-09-06 21:40:00	VALIDATED
6	1	6	2026-09-06 21:40:00	2200	70.00	55.00	65.00	73.33	2026-09-06 21:40:00	VALIDATED
7	1	7	2026-09-06 21:40:00	3900	150.00	60.00	98.00	97.50	2026-09-06 21:40:00	VALIDATED
8	1	8	2026-09-06 21:40:00	6800	200.00	90.00	100.00	95.77	2026-09-06 21:40:00	VALIDATED
9	1	1	2026-09-06 20:00:00	1800	80.00	50.00	45.00	45.00	2026-09-06 20:00:00	VALIDATED
10	1	2	2026-09-06 20:00:00	1700	75.00	48.00	44.00	42.50	2026-09-06 20:00:00	VALIDATED
11	1	3	2026-09-06 20:00:00	1600	70.00	45.00	41.00	45.71	2026-09-06 20:00:00	VALIDATED
12	1	4	2026-09-06 20:00:00	1900	85.00	50.00	48.00	47.50	2026-09-06 20:00:00	VALIDATED
13	1	5	2026-09-06 20:00:00	1300	60.00	40.00	36.00	37.14	2026-09-06 20:00:00	VALIDATED
14	1	6	2026-09-06 20:00:00	1200	55.00	38.00	35.00	40.00	2026-09-06 20:00:00	VALIDATED
15	1	7	2026-09-06 20:00:00	2000	90.00	45.00	50.00	50.00	2026-09-06 20:00:00	VALIDATED
16	1	8	2026-09-06 20:00:00	3500	120.00	60.00	52.00	49.30	2026-09-06 20:00:00	VALIDATED
130	1	2	2026-09-06 21:10:00	2867	105.45	66.60	71.37	71.66	2026-09-06 21:10:00	SIMULATED
131	1	2	2026-09-06 21:20:00	2989	114.00	72.00	74.42	74.73	2026-09-06 21:20:00	SIMULATED
132	1	2	2026-09-06 21:25:00	3038	114.00	72.00	75.64	75.95	2026-09-06 21:25:00	SIMULATED
133	1	2	2026-09-06 21:35:00	3144	119.70	75.60	79.43	78.59	2026-09-06 21:35:00	SIMULATED
134	1	3	2026-09-06 20:50:00	2436	90.00	55.00	62.20	69.60	2026-09-06 20:50:00	SIMULATED
135	1	3	2026-09-06 20:55:00	2523	90.00	55.00	64.40	72.07	2026-09-06 20:55:00	SIMULATED
136	1	3	2026-09-06 21:05:00	2679	99.90	61.05	68.40	76.54	2026-09-06 21:05:00	SIMULATED
137	1	3	2026-09-06 21:10:00	2750	99.90	61.05	70.20	78.56	2026-09-06 21:10:00	SIMULATED
138	1	3	2026-09-06 21:20:00	2867	108.00	66.00	73.20	81.91	2026-09-06 21:20:00	SIMULATED
139	1	3	2026-09-06 21:25:00	2914	108.00	66.00	74.40	83.26	2026-09-06 21:25:00	SIMULATED
140	1	3	2026-09-06 21:35:00	3031	113.40	69.30	77.30	86.59	2026-09-06 21:35:00	SIMULATED
141	1	4	2026-09-06 20:50:00	2903	120.00	62.00	72.57	72.57	2026-09-06 20:50:00	SIMULATED
142	1	4	2026-09-06 20:55:00	3005	120.00	62.00	75.13	75.13	2026-09-06 20:55:00	SIMULATED
143	1	4	2026-09-06 21:05:00	3192	133.20	68.82	79.80	79.80	2026-09-06 21:05:00	SIMULATED
144	1	4	2026-09-06 21:10:00	3276	133.20	68.82	81.90	81.90	2026-09-06 21:10:00	SIMULATED
145	1	4	2026-09-06 21:20:00	3416	144.00	74.40	85.40	85.40	2026-09-06 21:20:00	SIMULATED
24	1	1	2026-09-06 20:15:00	2100	90.00	55.00	52.00	52.50	2026-09-06 20:15:00	VALIDATED
25	1	2	2026-09-06 20:15:00	1950	85.00	50.00	49.00	48.75	2026-09-06 20:15:00	VALIDATED
26	1	3	2026-09-06 20:15:00	1850	80.00	48.00	47.00	52.86	2026-09-06 20:15:00	VALIDATED
27	1	4	2026-09-06 20:15:00	2200	95.00	55.00	55.00	55.00	2026-09-06 20:15:00	VALIDATED
28	1	5	2026-09-06 20:15:00	1500	65.00	42.00	40.00	42.86	2026-09-06 20:15:00	VALIDATED
29	1	6	2026-09-06 20:15:00	1400	60.00	40.00	38.00	46.67	2026-09-06 20:15:00	VALIDATED
30	1	7	2026-09-06 20:15:00	2300	100.00	48.00	58.00	57.50	2026-09-06 20:15:00	VALIDATED
31	1	8	2026-09-06 20:15:00	4000	140.00	65.00	59.00	56.34	2026-09-06 20:15:00	VALIDATED
32	1	1	2026-09-06 20:30:00	2400	100.00	60.00	60.00	60.00	2026-09-06 20:30:00	VALIDATED
33	1	2	2026-09-06 20:30:00	2200	90.00	55.00	55.00	55.00	2026-09-06 20:30:00	VALIDATED
34	1	3	2026-09-06 20:30:00	2100	85.00	50.00	54.00	60.00	2026-09-06 20:30:00	VALIDATED
35	1	4	2026-09-06 20:30:00	2500	110.00	60.00	63.00	62.50	2026-09-06 20:30:00	VALIDATED
36	1	5	2026-09-06 20:30:00	1750	70.00	45.00	46.00	50.00	2026-09-06 20:30:00	VALIDATED
37	1	6	2026-09-06 20:30:00	1600	65.00	42.00	44.00	53.33	2026-09-06 20:30:00	VALIDATED
38	1	7	2026-09-06 20:30:00	2700	115.00	50.00	68.00	67.50	2026-09-06 20:30:00	VALIDATED
39	1	8	2026-09-06 20:30:00	4500	155.00	70.00	67.00	63.38	2026-09-06 20:30:00	VALIDATED
40	1	1	2026-09-06 20:45:00	2700	110.00	65.00	68.00	67.50	2026-09-06 20:45:00	VALIDATED
41	1	1	2026-09-06 21:00:00	2997	122.10	72.15	75.48	74.93	2026-09-06 21:00:00	VALIDATED
42	1	1	2026-09-06 21:15:00	3240	132.00	78.00	81.60	81.00	2026-09-06 21:15:00	VALIDATED
43	1	1	2026-09-06 21:30:00	3402	138.60	81.90	85.68	85.05	2026-09-06 21:30:00	VALIDATED
44	1	2	2026-09-06 20:45:00	2450	95.00	60.00	61.00	61.25	2026-09-06 20:45:00	VALIDATED
45	1	2	2026-09-06 21:00:00	2720	105.45	66.60	67.71	67.99	2026-09-06 21:00:00	VALIDATED
46	1	2	2026-09-06 21:15:00	2940	114.00	72.00	73.20	73.50	2026-09-06 21:15:00	VALIDATED
47	1	2	2026-09-06 21:30:00	3087	119.70	75.60	76.86	77.18	2026-09-06 21:30:00	VALIDATED
48	1	3	2026-09-06 20:45:00	2350	90.00	55.00	60.00	67.14	2026-09-06 20:45:00	VALIDATED
49	1	3	2026-09-06 21:00:00	2609	99.90	61.05	66.60	74.53	2026-09-06 21:00:00	VALIDATED
50	1	3	2026-09-06 21:15:00	2820	108.00	66.00	72.00	80.57	2026-09-06 21:15:00	VALIDATED
51	1	3	2026-09-06 21:30:00	2961	113.40	69.30	75.60	84.60	2026-09-06 21:30:00	VALIDATED
52	1	4	2026-09-06 20:45:00	2800	120.00	62.00	70.00	70.00	2026-09-06 20:45:00	VALIDATED
53	1	4	2026-09-06 21:00:00	3108	133.20	68.82	77.70	77.70	2026-09-06 21:00:00	VALIDATED
54	1	4	2026-09-06 21:15:00	3360	144.00	74.40	84.00	84.00	2026-09-06 21:15:00	VALIDATED
55	1	4	2026-09-06 21:30:00	3528	151.20	78.12	88.20	88.20	2026-09-06 21:30:00	VALIDATED
146	1	4	2026-09-06 21:25:00	3472	144.00	74.40	86.80	86.80	2026-09-06 21:25:00	SIMULATED
147	1	4	2026-09-06 21:35:00	3664	151.20	78.12	91.60	91.60	2026-09-06 21:35:00	SIMULATED
148	1	5	2026-09-06 20:50:00	2022	75.00	48.00	53.91	57.75	2026-09-06 20:50:00	SIMULATED
149	1	5	2026-09-06 20:55:00	2093	75.00	48.00	55.81	59.80	2026-09-06 20:55:00	SIMULATED
150	1	5	2026-09-06 21:05:00	2223	83.25	53.28	59.28	63.51	2026-09-06 21:05:00	SIMULATED
151	1	5	2026-09-06 21:10:00	2282	83.25	53.28	60.84	65.19	2026-09-06 21:10:00	SIMULATED
152	1	5	2026-09-06 21:20:00	2379	90.00	57.60	63.44	67.97	2026-09-06 21:20:00	SIMULATED
153	1	5	2026-09-06 21:25:00	2418	90.00	57.60	64.48	69.09	2026-09-06 21:25:00	SIMULATED
154	1	5	2026-09-06 21:35:00	2479	94.50	60.48	67.76	70.82	2026-09-06 21:35:00	SIMULATED
155	1	6	2026-09-06 20:50:00	1866	70.00	45.00	49.76	62.20	2026-09-06 20:50:00	SIMULATED
156	1	6	2026-09-06 20:55:00	1932	70.00	45.00	51.52	64.40	2026-09-06 20:55:00	SIMULATED
157	1	6	2026-09-06 21:05:00	2052	77.70	49.95	54.72	68.40	2026-09-06 21:05:00	SIMULATED
158	1	6	2026-09-06 21:10:00	2106	77.70	49.95	56.16	70.20	2026-09-06 21:10:00	SIMULATED
159	1	6	2026-09-06 21:20:00	2196	84.00	54.00	58.56	73.20	2026-09-06 21:20:00	SIMULATED
160	1	6	2026-09-06 21:25:00	2232	84.00	54.00	59.52	74.40	2026-09-06 21:25:00	SIMULATED
161	1	6	2026-09-06 21:35:00	2234	88.20	56.70	62.74	74.47	2026-09-06 21:35:00	SIMULATED
162	1	7	2026-09-06 20:50:00	3214	125.00	52.00	80.86	80.34	2026-09-06 20:50:00	SIMULATED
163	1	7	2026-09-06 20:55:00	3327	125.00	52.00	83.72	83.19	2026-09-06 20:55:00	SIMULATED
164	1	7	2026-09-06 21:05:00	3534	138.75	57.72	88.92	88.35	2026-09-06 21:05:00	SIMULATED
165	1	7	2026-09-06 21:10:00	3627	138.75	57.72	91.26	90.68	2026-09-06 21:10:00	SIMULATED
166	1	7	2026-09-06 21:20:00	3782	150.00	62.40	95.16	94.55	2026-09-06 21:20:00	SIMULATED
167	1	7	2026-09-06 21:25:00	3844	150.00	62.40	96.72	96.10	2026-09-06 21:25:00	SIMULATED
168	1	7	2026-09-06 21:35:00	3903	157.50	65.52	98.14	97.58	2026-09-06 21:35:00	SIMULATED
169	1	8	2026-09-06 20:50:00	5183	170.00	75.00	76.71	73.00	2026-09-06 20:50:00	SIMULATED
170	1	8	2026-09-06 20:55:00	5367	170.00	75.00	79.43	75.59	2026-09-06 20:55:00	SIMULATED
171	1	8	2026-09-06 21:05:00	5700	188.70	83.25	84.36	80.28	2026-09-06 21:05:00	SIMULATED
56	1	5	2026-09-06 20:45:00	1950	75.00	48.00	52.00	55.71	2026-09-06 20:45:00	VALIDATED
57	1	5	2026-09-06 21:00:00	2165	83.25	53.28	57.72	61.84	2026-09-06 21:00:00	VALIDATED
58	1	5	2026-09-06 21:15:00	2340	90.00	57.60	62.40	66.86	2026-09-06 21:15:00	VALIDATED
59	1	5	2026-09-06 21:30:00	2457	94.50	60.48	65.52	70.20	2026-09-06 21:30:00	VALIDATED
60	1	6	2026-09-06 20:45:00	1800	70.00	45.00	48.00	60.00	2026-09-06 20:45:00	VALIDATED
61	1	6	2026-09-06 21:00:00	1998	77.70	49.95	53.28	66.60	2026-09-06 21:00:00	VALIDATED
62	1	6	2026-09-06 21:15:00	2160	84.00	54.00	57.60	72.00	2026-09-06 21:15:00	VALIDATED
63	1	6	2026-09-06 21:30:00	2268	88.20	56.70	60.48	75.60	2026-09-06 21:30:00	VALIDATED
64	1	7	2026-09-06 20:45:00	3100	125.00	52.00	78.00	77.50	2026-09-06 20:45:00	VALIDATED
65	1	7	2026-09-06 21:00:00	3441	138.75	57.72	86.58	86.03	2026-09-06 21:00:00	VALIDATED
66	1	7	2026-09-06 21:15:00	3720	150.00	62.40	93.60	93.00	2026-09-06 21:15:00	VALIDATED
67	1	7	2026-09-06 21:30:00	3906	157.50	65.52	98.28	97.65	2026-09-06 21:30:00	VALIDATED
68	1	8	2026-09-06 20:45:00	5000	170.00	75.00	74.00	70.42	2026-09-06 20:45:00	VALIDATED
69	1	8	2026-09-06 21:00:00	5550	188.70	83.25	82.14	78.17	2026-09-06 21:00:00	VALIDATED
70	1	8	2026-09-06 21:15:00	6000	204.00	90.00	88.80	84.51	2026-09-06 21:15:00	VALIDATED
71	1	8	2026-09-06 21:30:00	6300	214.20	94.50	93.24	88.73	2026-09-06 21:30:00	VALIDATED
172	1	8	2026-09-06 21:10:00	5850	188.70	83.25	86.58	82.40	2026-09-06 21:10:00	SIMULATED
173	1	8	2026-09-06 21:20:00	6100	204.00	90.00	90.28	85.92	2026-09-06 21:20:00	SIMULATED
174	1	8	2026-09-06 21:25:00	6200	204.00	90.00	91.76	87.32	2026-09-06 21:25:00	SIMULATED
175	1	8	2026-09-06 21:35:00	6550	214.20	94.50	96.62	92.25	2026-09-06 21:35:00	SIMULATED
\.


--
-- TOC entry 5950 (class 0 OID 24806)
-- Dependencies: 239
-- Data for Name: event_state; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.event_state (event_state_id, event_id, recorded_at, scenario, overall_status, crowd_level, transport_status, weather_status, active_incidents, risk_level, state_id, "timestamp", state_version, state_data, overall_risk_score, overall_risk_level, created_at) FROM stdin;
1	1	2026-09-06 21:40:00	COMBINED_CRISIS	ACTIVE	HIGH	DISRUPTED	HEAVY_RAIN	4	CRITICAL	\N	2026-09-06 21:40:00	1	\N	\N	CRITICAL	2026-09-06 19:46:28.278137
2	1	2026-09-06 18:00:00	NORMAL_EVENT	ACTIVE	LOW	NORMAL	CLEAR	0	LOW	\N	2026-09-06 18:00:00	1	\N	\N	LOW	2026-09-06 19:46:28.278137
3	1	2026-09-06 19:00:00	NORMAL_EVENT	ACTIVE	MEDIUM	NORMAL	CLOUDY	0	LOW	\N	2026-09-06 19:00:00	1	\N	\N	LOW	2026-09-06 19:46:28.278137
4	1	2026-09-06 20:00:00	CROWD_BUILDUP	ACTIVE	MEDIUM	NORMAL	CLOUDY	1	MEDIUM	\N	2026-09-06 20:00:00	1	\N	\N	MEDIUM	2026-09-06 19:46:28.278137
5	1	2026-09-06 20:30:00	CROWD_BUILDUP	ACTIVE	HIGH	BUSY	LIGHT_RAIN	0	MEDIUM	\N	2026-09-06 20:30:00	1	\N	\N	MEDIUM	2026-09-06 19:46:28.278137
6	1	2026-09-06 21:00:00	WEATHER_DISRUPTION	ACTIVE	HIGH	DISRUPTED	MODERATE_RAIN	2	HIGH	\N	2026-09-06 21:00:00	1	\N	\N	HIGH	2026-09-06 19:46:28.278137
7	1	2026-09-06 21:15:00	EXIT_CONGESTION	ACTIVE	HIGH	DISRUPTED	HEAVY_RAIN	3	CRITICAL	\N	2026-09-06 21:15:00	1	\N	\N	CRITICAL	2026-09-06 19:46:28.278137
8	1	2026-09-06 21:30:00	COMBINED_CRISIS	ACTIVE	CRITICAL	DISRUPTED	HEAVY_RAIN	2	CRITICAL	\N	2026-09-06 21:30:00	1	\N	\N	CRITICAL	2026-09-06 19:46:28.278137
9	1	2026-09-06 21:45:00	COMBINED_CRISIS	ACTIVE	CRITICAL	DISRUPTED	HEAVY_RAIN	4	CRITICAL	\N	2026-09-06 21:45:00	1	\N	\N	CRITICAL	2026-09-06 19:46:28.278137
10	1	2026-09-06 21:50:00	INTERVENTION_APPLIED	ACTIVE	HIGH	IMPROVING	HEAVY_RAIN	4	HIGH	\N	\N	2	{"source": "SIMULATED_SCENARIO", "action_id": 1, "intervention": "Additional shuttle service activated", "intervention_id": 2}	\N	HIGH	2026-09-07 02:13:23.025676
\.


--
-- TOC entry 5946 (class 0 OID 24777)
-- Dependencies: 235
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.events (event_id, venue_id, event_name, event_type, start_time, end_time, expected_attendance, name, status, scenario, data_status, created_at) FROM stdin;
1	1	Mega Event Demo - Wankhede	SPORTS	2026-09-06 18:00:00	2026-09-06 22:30:00	30000	Mega Event Demo - Wankhede	ACTIVE	\N	VALIDATED	2026-09-06 19:20:25.324944
\.


--
-- TOC entry 5944 (class 0 OID 24768)
-- Dependencies: 233
-- Data for Name: incidents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.incidents (incident_id, event_id, incident_type, description, severity, started_at, ended_at, entity_type, entity_id, location, status, reported_at) FROM stdin;
2	1	CROWD_CONGESTION	High crowd density near stadium exits	MEDIUM	2026-09-06 20:00:00	2026-09-06 20:30:00	ZONE	7	\N	RESOLVED	2026-09-06 20:00:00
3	1	TRANSPORT_CONGESTION	Public transport congestion near Churchgate area	HIGH	2026-09-06 20:45:00	2026-09-06 21:30:00	TRANSPORT_NODE	1	\N	RESOLVED	2026-09-06 20:45:00
1	1	TRANSPORT_DISRUPTION	Public transport congestion near stadium exits	HIGH	2026-09-06 21:35:00	\N	TRANSPORT_NODE	1	\N	ACTIVE	2026-09-06 21:35:00
4	1	HEAVY_RAIN	Heavy rainfall affecting crowd movement	HIGH	2026-09-06 21:00:00	\N	EVENT	1	\N	ACTIVE	2026-09-06 21:00:00
5	1	EXIT_BOTTLENECK	Slow crowd outflow detected at Gate 7	CRITICAL	2026-09-06 21:15:00	\N	ACCESS_POINT	7	\N	ACTIVE	2026-09-06 21:15:00
6	1	COMBINED_DISRUPTION	Crowd surge combined with rain and transport disruption	CRITICAL	2026-09-06 21:35:00	\N	EVENT	1	\N	ACTIVE	2026-09-06 21:35:00
\.


--
-- TOC entry 5956 (class 0 OID 24856)
-- Dependencies: 245
-- Data for Name: interventions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.interventions (intervention_id, event_id, created_at, intervention_name, intervention_type, description, target_area, priority, status, parameters, expected_risk_reduction, expected_capacity_change, people_benefited, time_saved_minutes, feasibility_score, cost_score, operational_impact, overall_score, rank) FROM stdin;
1	1	2026-09-06 21:44:00	Plan A - Open Alternate Exit	GATE_MANAGEMENT	Open alternate gate and redirect crowd flow.	Gate 6	HIGH	PROPOSED	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2	1	2026-09-06 21:44:00	Plan B - Increase Shuttle Service	TRANSPORT	Deploy additional shuttle buses toward major transport nodes.	Churchgate Area	HIGH	PROPOSED	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3	1	2026-09-06 21:44:00	Plan C - Crowd Diversion	CROWD_DIVERSION	Redirect crowd toward less congested exit zones.	Gate 6	MEDIUM	PROPOSED	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- TOC entry 5952 (class 0 OID 24819)
-- Dependencies: 241
-- Data for Name: predictions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.predictions (prediction_id, event_id, zone_id, created_at, prediction_type, predicted_value, prediction_unit, confidence_score, prediction_horizon_minutes, target_time, predicted_count, predicted_load_percentage, breach_eta_minutes, model_name, model_version, confidence) FROM stdin;
1	1	7	2026-09-06 21:42:00	CROWD_COUNT	4800.00	PERSONS	92.00	15	\N	\N	\N	\N	\N	\N	92.00
2	1	7	2026-09-06 21:42:00	CAPACITY_BREACH_PROBABILITY	94.00	PERCENT	91.00	15	\N	\N	\N	\N	\N	\N	91.00
\.


--
-- TOC entry 5954 (class 0 OID 24836)
-- Dependencies: 243
-- Data for Name: risk_assessments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.risk_assessments (risk_id, event_id, zone_id, assessed_at, risk_type, risk_score, risk_level, hotspot, explanation, entity_type, entity_id, component_scores, reason_signals) FROM stdin;
1	1	7	2026-09-06 21:43:00	CROWD_SURGE	92.00	CRITICAL	t	High crowd load combined with slow outflow and transport disruption.	ZONE	7	\N	\N
\.


--
-- TOC entry 5938 (class 0 OID 24737)
-- Dependencies: 227
-- Data for Name: routes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.routes (route_id, route_name, route_type, from_node_id, to_node_id, distance_km, estimated_time_minutes, route_geometry, name, capacity, current_load, travel_time_minutes, geometry, status, data_status) FROM stdin;
1	Churchgate to Marine Lines	RAILWAY	1	2	2	5	\N	Churchgate to Marine Lines	\N	\N	5	\N	\N	\N
2	Churchgate to CSMT	RAILWAY	1	3	3.5	8	\N	Churchgate to CSMT	\N	\N	8	\N	\N	\N
3	Churchgate to Mumbai Central	ROAD	1	4	4	20	\N	Churchgate to Mumbai Central	\N	\N	20	\N	\N	\N
4	Churchgate Station to Bus Point	WALKING	1	5	0.6	8	\N	Churchgate Station to Bus Point	\N	\N	8	\N	\N	\N
\.


--
-- TOC entry 5958 (class 0 OID 24872)
-- Dependencies: 247
-- Data for Name: simulations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.simulations (simulation_id, event_id, intervention_id, created_at, simulation_name, simulated_crowd_load, simulated_transport_load, simulated_risk_score, outcome, result_summary, simulation_data, before_state, after_state, affected_nodes, side_effects, feasible, simulation_score) FROM stdin;
1	1	1	2026-09-06 21:46:00	Simulation Plan A	82.00	88.00	68.00	IMPROVED	Risk reduced but transport congestion remains.	\N	\N	\N	\N	\N	\N	\N
2	1	2	2026-09-06 21:46:00	Simulation Plan B	72.00	60.00	48.00	BEST	Additional shuttle service significantly reduces transport pressure.	\N	\N	\N	\N	\N	\N	\N
3	1	3	2026-09-06 21:46:00	Simulation Plan C	78.00	82.00	61.00	IMPROVED	Crowd pressure reduced moderately.	\N	\N	\N	\N	\N	\N	\N
\.


--
-- TOC entry 5686 (class 0 OID 25247)
-- Dependencies: 253
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- TOC entry 5936 (class 0 OID 24730)
-- Dependencies: 225
-- Data for Name: transport_nodes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.transport_nodes (transport_node_id, node_name, node_type, latitude, longitude, capacity, location, current_load, load_percentage, status, data_status) FROM stdin;
2	Marine Lines Station	RAILWAY	18.9433	72.8234	12000	0101000020E6100000B1E1E995B23452401A51DA1B7CF13240	0	0.00	ACTIVE	VALIDATED
3	CSMT Station	RAILWAY	18.9402	72.8356	20000	0101000020E610000068226C787A355240FFB27BF2B0F03240	0	0.00	ACTIVE	VALIDATED
4	Mumbai Central Station	RAILWAY	18.9696	72.8194	18000	0101000020E6100000EA95B20C713452409C33A2B437F83240	0	0.00	ACTIVE	VALIDATED
5	Churchgate Bus Point	BUS	18.9348	72.8275	5000	0101000020E6100000295C8FC2F5345240014D840D4FEF3240	0	0.00	ACTIVE	VALIDATED
1	Churchgate Station	RAILWAY	18.9356	72.827	15000	0101000020E6100000B0726891ED3452403A234A7B83EF3240	13200	88.00	ACTIVE	SIMULATED
\.


--
-- TOC entry 5930 (class 0 OID 24692)
-- Dependencies: 219
-- Data for Name: venues; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.venues (venue_id, venue_name, address, capacity, latitude, longitude, location, name, venue_type, status, data_status, source) FROM stdin;
1	Wankhede Stadium	Wankhede Stadium, D Road, Churchgate, Mumbai - 400020, India	33100	18.9389	72.8258	0101000020E61000005B423EE8D9345240E3361AC05BF03240	Wankhede Stadium	\N	ACTIVE	VALIDATED	\N
\.


--
-- TOC entry 5932 (class 0 OID 24701)
-- Dependencies: 221
-- Data for Name: zones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.zones (zone_id, venue_id, zone_name, capacity, zone_type, boundary, name, parent_zone_id, status, data_status) FROM stdin;
1	1	North Stand	4000	SEATING	\N	North Stand	\N	ACTIVE	VALIDATED
2	1	Sunil Gavaskar Stand	4000	SEATING	\N	Sunil Gavaskar Stand	\N	ACTIVE	VALIDATED
3	1	Vijay Merchant Stand	3500	SEATING	\N	Vijay Merchant Stand	\N	ACTIVE	VALIDATED
4	1	Sachin Tendulkar Stand	4000	SEATING	\N	Sachin Tendulkar Stand	\N	ACTIVE	VALIDATED
5	1	MCA Stand	3500	SEATING	\N	MCA Stand	\N	ACTIVE	VALIDATED
6	1	Vitthal Divecha Stand	3000	SEATING	\N	Vitthal Divecha Stand	\N	ACTIVE	VALIDATED
7	1	Garware Stand	4000	SEATING	\N	Garware Stand	\N	ACTIVE	VALIDATED
8	1	Grand Stand	7100	PREMIUM	\N	Grand Stand	\N	ACTIVE	VALIDATED
\.


--
-- TOC entry 5986 (class 0 OID 0)
-- Dependencies: 222
-- Name: access_points_access_point_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.access_points_access_point_id_seq', 7, true);


--
-- TOC entry 5987 (class 0 OID 0)
-- Dependencies: 228
-- Name: accommodation_accommodation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.accommodation_accommodation_id_seq', 3, true);


--
-- TOC entry 5988 (class 0 OID 0)
-- Dependencies: 248
-- Name: applied_actions_action_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.applied_actions_action_id_seq', 1, true);


--
-- TOC entry 5989 (class 0 OID 0)
-- Dependencies: 250
-- Name: attendee_guidance_guidance_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.attendee_guidance_guidance_id_seq', 2, true);


--
-- TOC entry 5990 (class 0 OID 0)
-- Dependencies: 230
-- Name: conditions_condition_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.conditions_condition_id_seq', 8, true);


--
-- TOC entry 5991 (class 0 OID 0)
-- Dependencies: 236
-- Name: crowd_state_crowd_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.crowd_state_crowd_state_id_seq', 175, true);


--
-- TOC entry 5992 (class 0 OID 0)
-- Dependencies: 238
-- Name: event_state_event_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.event_state_event_state_id_seq', 10, true);


--
-- TOC entry 5993 (class 0 OID 0)
-- Dependencies: 234
-- Name: events_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.events_event_id_seq', 1, true);


--
-- TOC entry 5994 (class 0 OID 0)
-- Dependencies: 232
-- Name: incidents_incident_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.incidents_incident_id_seq', 6, true);


--
-- TOC entry 5995 (class 0 OID 0)
-- Dependencies: 244
-- Name: interventions_intervention_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.interventions_intervention_id_seq', 3, true);


--
-- TOC entry 5996 (class 0 OID 0)
-- Dependencies: 240
-- Name: predictions_prediction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.predictions_prediction_id_seq', 2, true);


--
-- TOC entry 5997 (class 0 OID 0)
-- Dependencies: 242
-- Name: risk_assessments_risk_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.risk_assessments_risk_id_seq', 1, true);


--
-- TOC entry 5998 (class 0 OID 0)
-- Dependencies: 226
-- Name: routes_route_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.routes_route_id_seq', 4, true);


--
-- TOC entry 5999 (class 0 OID 0)
-- Dependencies: 246
-- Name: simulations_simulation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.simulations_simulation_id_seq', 3, true);


--
-- TOC entry 6000 (class 0 OID 0)
-- Dependencies: 224
-- Name: transport_nodes_transport_node_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.transport_nodes_transport_node_id_seq', 5, true);


--
-- TOC entry 6001 (class 0 OID 0)
-- Dependencies: 218
-- Name: venues_venue_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.venues_venue_id_seq', 1, true);


--
-- TOC entry 6002 (class 0 OID 0)
-- Dependencies: 220
-- Name: zones_zone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.zones_zone_id_seq', 8, true);


--
-- TOC entry 5724 (class 2606 OID 24718)
-- Name: access_points access_points_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_points
    ADD CONSTRAINT access_points_pkey PRIMARY KEY (access_point_id);


--
-- TOC entry 5733 (class 2606 OID 24759)
-- Name: accommodation accommodation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accommodation
    ADD CONSTRAINT accommodation_pkey PRIMARY KEY (accommodation_id);


--
-- TOC entry 5754 (class 2606 OID 24899)
-- Name: applied_actions applied_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applied_actions
    ADD CONSTRAINT applied_actions_pkey PRIMARY KEY (action_id);


--
-- TOC entry 5756 (class 2606 OID 24919)
-- Name: attendee_guidance attendee_guidance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendee_guidance
    ADD CONSTRAINT attendee_guidance_pkey PRIMARY KEY (guidance_id);


--
-- TOC entry 5736 (class 2606 OID 24766)
-- Name: conditions conditions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.conditions
    ADD CONSTRAINT conditions_pkey PRIMARY KEY (condition_id);


--
-- TOC entry 5742 (class 2606 OID 24794)
-- Name: crowd_state crowd_state_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crowd_state
    ADD CONSTRAINT crowd_state_pkey PRIMARY KEY (crowd_state_id);


--
-- TOC entry 5744 (class 2606 OID 24812)
-- Name: event_state event_state_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_state
    ADD CONSTRAINT event_state_pkey PRIMARY KEY (event_state_id);


--
-- TOC entry 5740 (class 2606 OID 24782)
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (event_id);


--
-- TOC entry 5738 (class 2606 OID 24775)
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (incident_id);


--
-- TOC entry 5750 (class 2606 OID 24864)
-- Name: interventions interventions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interventions
    ADD CONSTRAINT interventions_pkey PRIMARY KEY (intervention_id);


--
-- TOC entry 5746 (class 2606 OID 24824)
-- Name: predictions predictions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.predictions
    ADD CONSTRAINT predictions_pkey PRIMARY KEY (prediction_id);


--
-- TOC entry 5748 (class 2606 OID 24844)
-- Name: risk_assessments risk_assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_assessments
    ADD CONSTRAINT risk_assessments_pkey PRIMARY KEY (risk_id);


--
-- TOC entry 5731 (class 2606 OID 24742)
-- Name: routes routes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_pkey PRIMARY KEY (route_id);


--
-- TOC entry 5752 (class 2606 OID 24879)
-- Name: simulations simulations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulations
    ADD CONSTRAINT simulations_pkey PRIMARY KEY (simulation_id);


--
-- TOC entry 5728 (class 2606 OID 24735)
-- Name: transport_nodes transport_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transport_nodes
    ADD CONSTRAINT transport_nodes_pkey PRIMARY KEY (transport_node_id);


--
-- TOC entry 5719 (class 2606 OID 24699)
-- Name: venues venues_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venues
    ADD CONSTRAINT venues_pkey PRIMARY KEY (venue_id);


--
-- TOC entry 5722 (class 2606 OID 24706)
-- Name: zones zones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones
    ADD CONSTRAINT zones_pkey PRIMARY KEY (zone_id);


--
-- TOC entry 5725 (class 1259 OID 26021)
-- Name: idx_access_points_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_access_points_location ON public.access_points USING gist (location);


--
-- TOC entry 5734 (class 1259 OID 26024)
-- Name: idx_accommodation_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_accommodation_location ON public.accommodation USING gist (location);


--
-- TOC entry 5729 (class 1259 OID 26025)
-- Name: idx_routes_geometry; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_routes_geometry ON public.routes USING gist (route_geometry);


--
-- TOC entry 5726 (class 1259 OID 26023)
-- Name: idx_transport_nodes_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transport_nodes_location ON public.transport_nodes USING gist (location);


--
-- TOC entry 5717 (class 1259 OID 26022)
-- Name: idx_venues_location; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_venues_location ON public.venues USING gist (location);


--
-- TOC entry 5720 (class 1259 OID 26026)
-- Name: idx_zones_boundary; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_zones_boundary ON public.zones USING gist (boundary);


--
-- TOC entry 5760 (class 2606 OID 24719)
-- Name: access_points access_points_venue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_points
    ADD CONSTRAINT access_points_venue_id_fkey FOREIGN KEY (venue_id) REFERENCES public.venues(venue_id);


--
-- TOC entry 5761 (class 2606 OID 24724)
-- Name: access_points access_points_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.access_points
    ADD CONSTRAINT access_points_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zones(zone_id);


--
-- TOC entry 5776 (class 2606 OID 24900)
-- Name: applied_actions applied_actions_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applied_actions
    ADD CONSTRAINT applied_actions_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id);


--
-- TOC entry 5777 (class 2606 OID 24905)
-- Name: applied_actions applied_actions_intervention_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.applied_actions
    ADD CONSTRAINT applied_actions_intervention_id_fkey FOREIGN KEY (intervention_id) REFERENCES public.interventions(intervention_id);


--
-- TOC entry 5778 (class 2606 OID 24920)
-- Name: attendee_guidance attendee_guidance_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendee_guidance
    ADD CONSTRAINT attendee_guidance_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id);


--
-- TOC entry 5766 (class 2606 OID 24795)
-- Name: crowd_state crowd_state_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crowd_state
    ADD CONSTRAINT crowd_state_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id);


--
-- TOC entry 5767 (class 2606 OID 24800)
-- Name: crowd_state crowd_state_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.crowd_state
    ADD CONSTRAINT crowd_state_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zones(zone_id);


--
-- TOC entry 5768 (class 2606 OID 24813)
-- Name: event_state event_state_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.event_state
    ADD CONSTRAINT event_state_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id);


--
-- TOC entry 5765 (class 2606 OID 24783)
-- Name: events events_venue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_venue_id_fkey FOREIGN KEY (venue_id) REFERENCES public.venues(venue_id);


--
-- TOC entry 5764 (class 2606 OID 26027)
-- Name: incidents fk_incidents_event; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT fk_incidents_event FOREIGN KEY (event_id) REFERENCES public.events(event_id);


--
-- TOC entry 5773 (class 2606 OID 24865)
-- Name: interventions interventions_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interventions
    ADD CONSTRAINT interventions_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id);


--
-- TOC entry 5769 (class 2606 OID 24825)
-- Name: predictions predictions_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.predictions
    ADD CONSTRAINT predictions_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id);


--
-- TOC entry 5770 (class 2606 OID 24830)
-- Name: predictions predictions_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.predictions
    ADD CONSTRAINT predictions_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zones(zone_id);


--
-- TOC entry 5771 (class 2606 OID 24845)
-- Name: risk_assessments risk_assessments_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_assessments
    ADD CONSTRAINT risk_assessments_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id);


--
-- TOC entry 5772 (class 2606 OID 24850)
-- Name: risk_assessments risk_assessments_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_assessments
    ADD CONSTRAINT risk_assessments_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zones(zone_id);


--
-- TOC entry 5762 (class 2606 OID 24743)
-- Name: routes routes_from_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_from_node_id_fkey FOREIGN KEY (from_node_id) REFERENCES public.transport_nodes(transport_node_id);


--
-- TOC entry 5763 (class 2606 OID 24748)
-- Name: routes routes_to_node_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_to_node_id_fkey FOREIGN KEY (to_node_id) REFERENCES public.transport_nodes(transport_node_id);


--
-- TOC entry 5774 (class 2606 OID 24880)
-- Name: simulations simulations_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulations
    ADD CONSTRAINT simulations_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(event_id);


--
-- TOC entry 5775 (class 2606 OID 24885)
-- Name: simulations simulations_intervention_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.simulations
    ADD CONSTRAINT simulations_intervention_id_fkey FOREIGN KEY (intervention_id) REFERENCES public.interventions(intervention_id);


--
-- TOC entry 5759 (class 2606 OID 24707)
-- Name: zones zones_venue_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones
    ADD CONSTRAINT zones_venue_id_fkey FOREIGN KEY (venue_id) REFERENCES public.venues(venue_id);


-- Completed on 2026-09-07 21:08:30

--
-- PostgreSQL database dump complete
--

