import { useEffect, useMemo, useState } from "react";
import {
  Link,
  Route,
  Switch,
  Router as WouterRouter,
  useLocation,
  useParams,
} from "wouter";

import {
  ArrowRight,
  BedDouble,
  CalendarDays,
  Check,
  ChevronLeft,
  CircleAlert,
  CircleCheck,
  Clock3,
  Compass,
  Heart,
  HousePlus,
  LoaderCircle,
  LogOut,
  Menu,
  Moon,
  Mountain,
  Plus,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Star,
  Sun,
  TicketCheck,
  UserRound,
  UsersRound,
  WalletCards,
  X,
} from "lucide-react";

import { api } from "./api";


// ============================================================
// MONEY
// ============================================================

const money = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 2,
});


// ============================================================
// DATE
// ============================================================

const dateText = (value) =>
  value
    ? new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
      }).format(new Date(value))
    : "—";


// ============================================================
// GENERIC RESOURCE LOADER
// ============================================================

function useResource(loader, deps = []) {
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let active = true;

    setState((current) => ({
      ...current,
      loading: true,
      error: null,
    }));

    loader()
      .then((data) => {
        if (active) {
          setState({
            data,
            loading: false,
            error: null,
          });
        }
      })
      .catch((error) => {
        if (active) {
          setState({
            data: null,
            loading: false,
            error,
          });
        }
      });

    return () => {
      active = false;
    };
  }, deps);

  return state;
}


// ============================================================
// BRAND
// ============================================================

function Brand() {
  return (
    <Link href="/" className="brand">
      <span className="brand-mark">
        <Compass size={19} />
      </span>

      <span>
        staywise
        <span className="brand-dot">.</span>
      </span>
    </Link>
  );
}


// ============================================================
// HEADER
// ============================================================

function Header() {
  const [location, setLocation] = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  const [dark, setDark] = useState(
    () =>
      localStorage.getItem("staywise_theme") === "dark"
  );

  const token = localStorage.getItem(
    "staywise_token"
  );

  const user = useResource(
    () =>
      token
        ? api.me()
        : Promise.resolve(null),
    [token]
  );

  useEffect(() => {
    document.documentElement.classList.toggle(
      "dark",
      dark
    );

    localStorage.setItem(
      "staywise_theme",
      dark ? "dark" : "light"
    );
  }, [dark]);

  const logout = () => {
    localStorage.removeItem("staywise_token");

    setLocation("/");

    window.location.reload();
  };

  const isOwnerAccount =
    user.data?.role === "owner";

  const isOwnerSection =
    location.startsWith("/owner");

  return (
    <header className="site-header">
      <div className="container header-inner">

        <Brand />

        <nav className="desktop-nav">

          <Link
            href="/hotels"
            className={
              location === "/hotels"
                ? "active"
                : ""
            }
          >
            Discover stays
          </Link>

          {isOwnerAccount && (
            <Link
              href="/owner/dashboard"
              className={
                isOwnerSection
                  ? "active"
                  : ""
              }
            >
              For hosts
            </Link>
          )}

        </nav>


        <div className="header-actions desktop-nav">

          <button
            className="icon-button"
            onClick={() => setDark(!dark)}
            aria-label="Toggle theme"
          >
            {dark ? (
              <Sun size={17} />
            ) : (
              <Moon size={17} />
            )}
          </button>


          {user.data ? (
            <>
              <Link
                href={
                  user.data.role === "owner"
                    ? "/owner/dashboard"
                    : "/dashboard"
                }
                className="user-chip"
              >
                <span>
                  {user.data.name.slice(0, 1)}
                </span>

                {user.data.name.split(" ")[0]}
              </Link>

              <button
                className="icon-button"
                onClick={logout}
                aria-label="Log out"
              >
                <LogOut size={17} />
              </button>
            </>
          ) : (
            <>
              <Link href="/login">
                Log in
              </Link>

              <Link
                href="/register"
                className="button small secondary"
              >
                Join Staywise
              </Link>
            </>
          )}

        </div>


        <button
          className="menu-button"
          onClick={() =>
            setMenuOpen(!menuOpen)
          }
          aria-label="Open menu"
        >
          <Menu size={22} />
        </button>

      </div>


      {menuOpen && (
        <div className="mobile-menu">

          <Link
            href="/hotels"
            onClick={() =>
              setMenuOpen(false)
            }
          >
            Discover stays
          </Link>

          {isOwnerAccount && (
            <Link
              href="/owner/dashboard"
              onClick={() =>
                setMenuOpen(false)
              }
            >
              For hosts
            </Link>
          )}

          <Link
            href="/refund-policy"
            onClick={() =>
              setMenuOpen(false)
            }
          >
            Refund policy
          </Link>

          <button
            onClick={() =>
              setDark(!dark)
            }
          >
            {dark ? (
              <Sun size={16} />
            ) : (
              <Moon size={16} />
            )}

            {dark
              ? "Light theme"
              : "Dark theme"}
          </button>

          {user.data ? (
            <Link href="/dashboard">
              Your account
            </Link>
          ) : (
            <Link href="/login">
              Log in
            </Link>
          )}

        </div>
      )}

    </header>
  );
}


// ============================================================
// FOOTER
// ============================================================

function Footer() {
  const health = useResource(api.health);

  return (
    <footer className="footer">

      <div className="container footer-grid">

        <div>
          <Brand />

          <p>
            A better way to find the places
            that make a trip worth taking.
          </p>

          <small>
            {health.data?.status === "ok"
              ? "All systems ready"
              : "Staywise, always curious"}
          </small>
        </div>


        <div>
          <b>Explore</b>

          <Link href="/hotels">
            All stays
          </Link>

          <Link href="/">
            Inspiration
          </Link>

          <Link href="/refund-policy">
            Refund policy
          </Link>
        </div>


        <div>
          <b>Host</b>

          <Link href="/owner/login">
            Owner login
          </Link>

          <Link href="/owner/register">
            List your place
          </Link>
        </div>


        <div>
          <b>A small promise</b>

          <p>
            Clear prices. Human places.
            No guesswork.
          </p>
        </div>

      </div>


      <div className="container footer-bottom">
        © 2025 Staywise · Built for better weekends
      </div>

    </footer>
  );
}


// ============================================================
// REFUND POLICY FLOATING TAB
// ============================================================

function RefundPolicyTab() {
  return (
    <Link
      href="/refund-policy"
      className="refund-policy-tab"
      aria-label="View refund and cancellation policy"
    >
      <ShieldCheck size={16} />

      <span>
        Refund policy
      </span>
    </Link>
  );
}


// ============================================================
// PAGE WRAPPER
// ============================================================

function Page({
  children,
  footer = true,
}) {
  return (
    <div className="page">

      <Header />

      {children}

      <RefundPolicyTab />

      {footer && <Footer />}

    </div>
  );
}


// ============================================================
// SEARCH BAR
// ============================================================

function SearchBar({
  compact = false,
}) {
  const [, navigate] = useLocation();

  const [form, setForm] = useState({
    destination: "",
    checkIn: "",
    checkOut: "",
    guests: "2",
  });

  const submit = (event) => {
    event.preventDefault();

    const query =
      new URLSearchParams(
        Object.entries(form).filter(
          ([, value]) => value
        )
      );

    navigate(`/hotels?${query}`);
  };

  return (
    <form
      className={`search-bar ${
        compact ? "compact" : ""
      }`}
      onSubmit={submit}
    >

      <label>
        <Search size={18} />

        <span>
          Where

          <input
            placeholder="City or country"
            value={form.destination}
            onChange={(e) =>
              setForm({
                ...form,
                destination:
                  e.target.value,
              })
            }
          />
        </span>
      </label>


      <label>
        <CalendarDays size={17} />

        <span>
          Check in

          <input
            type="date"
            value={form.checkIn}
            onChange={(e) =>
              setForm({
                ...form,
                checkIn:
                  e.target.value,
              })
            }
          />
        </span>
      </label>


      <label>
        <CalendarDays size={17} />

        <span>
          Check out

          <input
            type="date"
            value={form.checkOut}
            onChange={(e) =>
              setForm({
                ...form,
                checkOut:
                  e.target.value,
              })
            }
          />
        </span>
      </label>


      <label>
        <UsersRound size={17} />

        <span>
          Guests

          <input
            type="number"
            min="1"
            value={form.guests}
            onChange={(e) =>
              setForm({
                ...form,
                guests:
                  e.target.value,
              })
            }
          />
        </span>
      </label>


      <button className="button primary">
        <Search size={17} />
        Search
      </button>

    </form>
  );
}


// ============================================================
// IMAGE
// ============================================================

function ImageOrGradient({
  src,
  alt,
  className = "",
}) {
  return src ? (
    <img
      className={`cover ${className}`}
      src={src}
      alt={alt}
    />
  ) : (
    <div
      className={`image-gradient ${className}`}
      role="img"
      aria-label={alt}
    />
  );
}


// ============================================================
// HOTEL CARD
// ============================================================

function HotelCard({
  hotel,
  index = 0,
}) {
  const [saved, setSaved] =
    useState(
      () =>
        localStorage.getItem(
          `staywise_fav_${hotel.id}`
        ) === "1"
    );

  const toggle = () => {
    const next = !saved;

    setSaved(next);

    localStorage.setItem(
      `staywise_fav_${hotel.id}`,
      next ? "1" : "0"
    );
  };

  return (
    <article
      className={`hotel-card delay-${Math.min(
        index,
        2
      )}`}
    >

      <div className="hotel-image-wrap">

        <Link
          href={`/hotels/${hotel.id}`}
        >
          <ImageOrGradient
            src={hotel.image}
            alt={hotel.name}
            className="hotel-image"
          />
        </Link>


        <button
          className={`favorite ${
            saved ? "saved" : ""
          }`}
          onClick={toggle}
          aria-label="Save favorite"
        >
          <Heart
            size={17}
            fill={
              saved
                ? "currentColor"
                : "none"
            }
          />
        </button>


        <span className="pill image-pill">
          {hotel.propertyType}
        </span>

      </div>


      <Link
        href={`/hotels/${hotel.id}`}
        className="hotel-card-copy"
      >

        <div className="row">

          <h3>
            {hotel.name}
          </h3>

          <span className="rating">
            <Star
              size={14}
              fill="currentColor"
            />

            {hotel.rating.toFixed(1)}
          </span>

        </div>


        <p>
          {hotel.location},{" "}
          {hotel.city}
        </p>


        <strong>
          {money.format(
            hotel.priceFrom
          )}

          <em>
            {" "}
            / night
          </em>
        </strong>

      </Link>

    </article>
  );
}


// ============================================================
// HOME
// ============================================================

function HomePage() {
  const result =
    useResource(
      () => api.hotels(),
      []
    );

  const hotels =
    result.data || [];

  return (
    <Page>

      <main>

        <section className="hero">

          <div className="container hero-grid">

            <div className="hero-copy">

              <p className="eyebrow">
                <Sparkles size={14} />
                Stays with a point of view
              </p>

              <h1>
                Go somewhere
                <br />
                <span>
                  worth staying.
                </span>
              </h1>

              <p className="hero-subtitle">
                Find the little places with
                big character — from a
                cliffside cabin to a city
                apartment with the perfect
                morning light.
              </p>

            </div>


            <div className="hero-art">

              <div className="art-shape shape-one" />

              <div className="art-shape shape-two" />

              <div className="art-shape shape-three">
                <Mountain size={76} />
              </div>

              <b>
                stay curious.
              </b>

            </div>

          </div>


          <div className="container hero-search">
            <SearchBar />
          </div>

        </section>


        <section className="container section featured">

          <div className="section-heading">

            <div>
              <p className="eyebrow">
                Handpicked by us
              </p>

              <h2>
                Places that linger.
              </h2>
            </div>

            <Link
              href="/hotels"
              className="text-link"
            >
              See all stays
              <ArrowRight size={16} />
            </Link>

          </div>


          {result.loading ? (
            <Skeletons />
          ) : (
            <div className="hotel-grid">

              {hotels
                .slice(0, 3)
                .map(
                  (hotel, index) => (
                    <HotelCard
                      hotel={hotel}
                      index={index}
                      key={hotel.id}
                    />
                  )
                )}

            </div>
          )}

        </section>


        <section className="container standard-grid">

          <div className="standard-card">

            <p className="eyebrow accent">
              The Staywise standard
            </p>

            <h2>
              A little more human.
            </h2>

            <p>
              No anonymous towers.
              We look for thoughtful
              hosts, honest photos,
              and the details you
              remember on the way home.
            </p>

            <Link
              href="/hotels"
              className="button accent-button"
            >
              Explore the standard
              <ArrowRight size={16} />
            </Link>

          </div>


          <div className="feature-grid">

            <Feature
              icon={<ShieldCheck />}
              title="Clear by default"
              text="What you see is what you pay. No tiny surprises at checkout."
            />

            <Feature
              icon={<Heart />}
              title="Picked with care"
              text="Our collection favors places with a real sense of place."
            />

            <Feature
              icon={<TicketCheck />}
              title="Easy when plans move"
              text="Simple policies, clear booking details, less back-and-forth."
            />

            <Feature
              icon={<HousePlus />}
              title="Good for hosts"
              text="Independent owners get tools that respect their time."
            />

          </div>

        </section>


        <section className="container host-callout">

          <div>

            <p className="eyebrow">
              For good hosts
            </p>

            <h2>
              Your place has a story.
              <br />
              Let it be found.
            </h2>

          </div>


          <div>

            <p>
              Staywise gives independent
              owners a clear way to put
              their best foot forward —
              and guests a reason to book
              with confidence.
            </p>

            <Link
              href="/owner/register"
              className="button secondary"
            >
              List your place
              <ArrowRight size={16} />
            </Link>

          </div>

        </section>

      </main>

    </Page>
  );
}


// ============================================================
// FEATURE
// ============================================================

function Feature({
  icon,
  title,
  text,
}) {
  return (
    <div className="feature-card">

      <span>
        {icon}
      </span>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

    </div>
  );
}


// ============================================================
// SKELETON
// ============================================================

function Skeletons() {
  return (
    <div className="hotel-grid">

      {[1, 2, 3].map(
        (item) => (
          <div
            className="skeleton-card"
            key={item}
          >
            <div />
            <b />
            <i />
          </div>
        )
      )}

    </div>
  );
}


// ============================================================
// EMPTY
// ============================================================

function Empty({
  title,
  text,
  action,
  href = "/hotels",
}) {
  return (
    <div className="empty">

      <Compass size={24} />

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

      {action && (
        <Link
          href={href}
          className="button secondary"
        >
          {action}
        </Link>
      )}

    </div>
  );
}


// ============================================================
// HOTELS PAGE
// ============================================================

function HotelsPage() {
  const [location, navigate] =
    useLocation();

  const query =
    new URLSearchParams(
      location.split("?")[1] || ""
    );

  const [filters, setFilters] =
    useState({
      destination:
        query.get("destination") || "",
      propertyType: "",
      minPrice: "",
      maxPrice: "",
      sort:
        query.get("sort") ||
        "recommended",
    });

  const result = useResource(
    () =>
      api.hotels({
        ...filters,
        guests:
          query.get("guests") || 1,
        checkIn:
          query.get("checkIn") || "",
        checkOut:
          query.get("checkOut") || "",
      }),
    [
      filters.destination,
      filters.propertyType,
      filters.minPrice,
      filters.maxPrice,
      filters.sort,
      location,
    ]
  );

  const hotels =
    result.data || [];

  const clear = () => {
    setFilters({
      destination: "",
      propertyType: "",
      minPrice: "",
      maxPrice: "",
      sort: "recommended",
    });

    navigate("/hotels");
  };

  return (
    <Page>

      <main className="container content">

        <div className="page-heading">

          <div>

            <p className="eyebrow">
              The collection
            </p>

            <h1>
              Find your next stay.
            </h1>

            <p>
              {result.loading
                ? "Searching the map…"
                : `${hotels.length} places ready when you are`}
            </p>

          </div>


          <Link
            href="/"
            className="text-link"
          >
            <ChevronLeft size={16} />
            Back to inspiration
          </Link>

        </div>


        <SearchBar compact />


        <div className="listing-layout">

          <aside className="filters">

            <div className="row">

              <h3>
                Tune it
              </h3>

              <SlidersHorizontal size={18} />

            </div>


            <label>
              Property type

              <select
                value={filters.propertyType}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    propertyType:
                      e.target.value,
                  })
                }
              >
                <option value="">
                  Everything
                </option>

                <option>
                  Hotel
                </option>

                <option>
                  Cabin
                </option>

                <option>
                  Villa
                </option>

                <option>
                  Apartment
                </option>
              </select>
            </label>


            <label>
              Nightly price

              <div className="price-fields">

                <input
                  type="number"
                  placeholder="From"
                  value={filters.minPrice}
                  onChange={(e) =>
                    setFilters({
                      ...filters,
                      minPrice:
                        e.target.value,
                    })
                  }
                />

                <input
                  type="number"
                  placeholder="To"
                  value={filters.maxPrice}
                  onChange={(e) =>
                    setFilters({
                      ...filters,
                      maxPrice:
                        e.target.value,
                    })
                  }
                />

              </div>

            </label>


            <button
              className="text-link"
              onClick={clear}
            >
              Clear all
            </button>

          </aside>


          <section className="results">

            <div className="results-top">

              <span>
                <b>
                  {hotels.length}
                </b>{" "}
                stays
              </span>


              <label>
                Sort by

                <select
                  value={filters.sort}
                  onChange={(e) => {
                    setFilters({
                      ...filters,
                      sort: e.target.value,
                    });

                    navigate(
                      `/hotels?sort=${e.target.value}`
                    );
                  }}
                >
                  <option value="recommended">
                    Recommended
                  </option>

                  <option value="price_low">
                    Price: low to high
                  </option>

                  <option value="price_high">
                    Price: high to low
                  </option>

                  <option value="rating">
                    Guest rating
                  </option>
                </select>

              </label>

            </div>


            {result.loading ? (
              <Skeletons />
            ) : result.error ? (
              <Empty
                title="The search took a wrong turn."
                text={result.error.message}
                action="Try again"
              />
            ) : hotels.length ? (
              <div className="hotel-grid two">

                {hotels.map(
                  (hotel, index) => (
                    <HotelCard
                      hotel={hotel}
                      index={index}
                      key={hotel.id}
                    />
                  )
                )}

              </div>
            ) : (
              <Empty
                title="Nothing quite there yet"
                text="Try a nearby city or loosen one of the filters. Your good weekend is still out there."
                action="Clear filters"
              />
            )}

          </section>

        </div>

      </main>

    </Page>
  );
}


// ============================================================
// HOTEL DETAILS
// ============================================================

function HotelDetailsPage() {
  const { hotelId } =
    useParams();

  const result =
    useResource(
      () => api.hotel(hotelId),
      [hotelId]
    );

  const [selectedRoom, setSelectedRoom] =
    useState("");

  const [bookOpen, setBookOpen] =
    useState(false);

  if (result.loading) {
    return (
      <Page>
        <main className="container content">
          <Skeletons />
        </main>
      </Page>
    );
  }

  if (
    result.error ||
    !result.data
  ) {
    return (
      <Page>
        <main className="container content">
          <Empty
            title="This stay is off the map"
            text={
              result.error?.message ||
              "Hotel not found"
            }
            action="Browse all stays"
          />
        </main>
      </Page>
    );
  }

  const hotel = result.data;

  return (
    <Page>

      <main className="container content">

        <Link
          href="/hotels"
          className="text-link back-link"
        >
          <ChevronLeft size={16} />
          All stays
        </Link>


        <div className="detail-gallery">

          <ImageOrGradient
            src={
              hotel.images?.[0] ||
              hotel.image
            }
            alt={hotel.name}
          />

          <div>

            {(hotel.images || [])
              .slice(1, 5)
              .map(
                (image, i) => (
                  <ImageOrGradient
                    src={image}
                    alt={`${hotel.name} view ${
                      i + 2
                    }`}
                    key={image}
                  />
                )
              )}

          </div>

        </div>


        <div className="detail-layout">

          <section>

            <p className="eyebrow">
              {hotel.propertyType}
              {" · "}
              {hotel.city},{" "}
              {hotel.country}
            </p>


            <div className="detail-title row">

              <div>

                <h1>
                  {hotel.name}
                </h1>

                <p className="muted">

                  <Star
                    size={15}
                    fill="currentColor"
                  />

                  <b>
                    {hotel.rating.toFixed(1)}
                  </b>

                  {" · "}
                  {hotel.reviews} reviews
                  {" · "}
                  {hotel.location}

                </p>

              </div>


              <button
                className="button outline"
                onClick={() =>
                  navigator.clipboard?.writeText(
                    window.location.href
                  )
                }
              >
                Share
              </button>

            </div>


            <p className="description">
              {hotel.description}
            </p>


            <div className="detail-block">

              <h2>
                What you’ll find here
              </h2>

              <div className="amenities">

                {hotel.amenities?.map(
                  (item) => (
                    <span key={item}>
                      {item}
                    </span>
                  )
                )}

              </div>

            </div>


            <div className="detail-columns">

              <div>

                <p className="eyebrow">
                  House policies
                </p>

                <p>
                  Check in from{" "}
                  {hotel.policies?.checkIn}

                  <br />

                  Check out by{" "}
                  {hotel.policies?.checkOut}

                  <br />

                  {hotel.policies?.cancellation}
                </p>

              </div>


              <div>

                <p className="eyebrow">
                  Around the stay
                </p>

                <p>
                  {hotel.nearby?.join(
                    " · "
                  )}
                </p>

              </div>

            </div>

          </section>


          <aside className="booking-card">

            <p className="eyebrow">
              From
            </p>

            <h2>
              {money.format(
                hotel.priceFrom
              )}

              <small>
                / night
              </small>
            </h2>

            <hr />

            <h3>
              Choose your room
            </h3>


            {hotel.rooms?.map(
              (room) => (
                <button
                  className={`room-option ${
                    selectedRoom === room.id
                      ? "selected"
                      : ""
                  }`}
                  key={room.id}
                  onClick={() =>
                    setSelectedRoom(
                      room.id
                    )
                  }
                >

                  <span>

                    <b>
                      {room.name}
                    </b>

                    <small>
                      {room.beds} bed ·
                      up to{" "}
                      {room.maxGuests} guests
                    </small>

                  </span>


                  <strong>
                    {money.format(
                      room.pricePerNight
                    )}
                  </strong>

                </button>
              )
            )}


            <button
              className="button primary full"
              disabled={
                !hotel.rooms?.length
              }
              onClick={() => {
                setSelectedRoom(
                  selectedRoom ||
                    hotel.rooms[0]?.id
                );

                setBookOpen(true);
              }}
            >
              Reserve this stay
              <ArrowRight size={17} />
            </button>

          </aside>

        </div>

      </main>


      {bookOpen && (
        <BookingModal
          hotel={hotel}
          roomId={selectedRoom}
          close={() =>
            setBookOpen(false)
          }
        />
      )}

    </Page>
  );
}


// ============================================================
// BOOKING MODAL
// ============================================================

function BookingModal({
  hotel,
  roomId,
  close,
}) {
  const [, navigate] =
    useLocation();

  const room =
    hotel.rooms.find(
      (item) =>
        item.id === roomId
    ) ||
    hotel.rooms[0];

  const [form, setForm] =
    useState({
      checkIn: "",
      checkOut: "",
      guests: "2",
      numberOfRooms: "1",
    });

  const [error, setError] =
    useState("");

  const [saving, setSaving] =
    useState(false);

  const submit = async (
    event
  ) => {
    event.preventDefault();

    setError("");
    setSaving(true);

    try {
      const booking =
        await api.createBooking({
          hotelId: hotel.id,
          roomId: room.id,
          ...form,
          guests: Number(
            form.guests
          ),
          numberOfRooms:
            Number(
              form.numberOfRooms
            ),
        });

      navigate(
        `/booking/${booking.id}`
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop">

      <div className="modal">

        <button
          className="modal-close"
          onClick={close}
        >
          <X size={19} />
        </button>


        <p className="eyebrow">
          Almost yours
        </p>

        <h2>
          {room.name}
        </h2>

        <p className="muted">
          {hotel.name}
        </p>


        <form onSubmit={submit}>

          <div className="form-grid">

            <Field
              label="Check in"
              type="date"
              value={form.checkIn}
              onChange={(value) =>
                setForm({
                  ...form,
                  checkIn: value,
                })
              }
            />

            <Field
              label="Check out"
              type="date"
              value={form.checkOut}
              onChange={(value) =>
                setForm({
                  ...form,
                  checkOut: value,
                })
              }
            />

            <Field
              label="Guests"
              type="number"
              value={form.guests}
              onChange={(value) =>
                setForm({
                  ...form,
                  guests: value,
                })
              }
            />

            <Field
              label="Rooms"
              type="number"
              value={
                form.numberOfRooms
              }
              onChange={(value) =>
                setForm({
                  ...form,
                  numberOfRooms: value,
                })
              }
            />

          </div>


          {error && (
            <p className="error">

              <CircleAlert size={16} />

              {error}

            </p>
          )}


          <p className="notice">

            {money.format(
              room.pricePerNight
            )}{" "}
            × night

            <br />

            <small>
              You’ll review the full
              total before payment.
            </small>

          </p>


          <button
            className="button primary full"
            disabled={saving}
          >

            {saving && (
              <LoaderCircle
                size={17}
                className="spin"
              />
            )}

            Continue to booking

          </button>

        </form>

      </div>

    </div>
  );
}


// ============================================================
// FIELD
// ============================================================

function Field({
  label,
  value,
  onChange,
  type = "text",
  placeholder = "",
}) {
  return (
    <label className="field">

      <span>
        {label}
      </span>

      <input
        required
        min={
          type === "number"
            ? 1
            : undefined
        }
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={(e) =>
          onChange(
            e.target.value
          )
        }
      />

    </label>
  );
}


// ============================================================
// AUTH
// ============================================================

function AuthPage({
  owner = false,
  register = false,
}) {
  const [, navigate] =
    useLocation();

  const [form, setForm] =
    useState({
      name: "",
      email: "",
      password: "",
    });

  const [error, setError] =
    useState("");

  const [saving, setSaving] =
    useState(false);

  const submit = async (
    event
  ) => {
    event.preventDefault();

    setError("");
    setSaving(true);

    try {
      const response =
        register
          ? await api.register({
              ...form,
              role: owner
                ? "owner"
                : "guest",
            })
          : await api.login({
              email: form.email,
              password:
                form.password,
            });

      localStorage.setItem(
        "staywise_token",
        response.token
      );

      const role =
        response.user?.role;

      navigate(
        role === "owner"
          ? "/owner/dashboard"
          : "/dashboard"
      );

      window.location.reload();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const eyebrow =
    register
      ? owner
        ? "The host side"
        : "The guest side"
      : "Good to see you";

  const heading =
    register
      ? owner
        ? "Make your place the one they remember."
        : "Your next good story starts here."
      : "Welcome back.";

  const sideText =
    register
      ? owner
        ? "A straightforward toolkit for independent hosts who care about the details."
        : "Keep your trips, favorites, and little escapes in one thoughtful place."
      : "Log in once — guests and hosts both use this page, and you'll land on the right dashboard automatically.";

  return (
    <Page>

      <main className="auth-layout">

        <div className="auth-side">

          <p className="eyebrow accent">
            {eyebrow}
          </p>

          <h1>
            {heading}
          </h1>

          <p>
            {sideText}
          </p>

        </div>


        <div className="auth-form">

          <p className="eyebrow">
            {register
              ? "Start here"
              : "Good to see you"}
          </p>

          <h2>
            {register
              ? "Create your account."
              : "Come on in."}
          </h2>

          <p className="muted">
            {register
              ? "It only takes a minute to get moving."
              : "Your saved places and plans are waiting."}
          </p>


          <form onSubmit={submit}>

            {register && (
              <Field
                label="Full name"
                placeholder="How should we call you?"
                value={form.name}
                onChange={(value) =>
                  setForm({
                    ...form,
                    name: value,
                  })
                }
              />
            )}


            <Field
              label="Email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={(value) =>
                setForm({
                  ...form,
                  email: value,
                })
              }
            />


            <Field
              label="Password"
              type="password"
              placeholder="At least 6 characters"
              value={form.password}
              onChange={(value) =>
                setForm({
                  ...form,
                  password: value,
                })
              }
            />


            {error && (
              <p className="error">
                {error}
              </p>
            )}


            <button
              className="button primary full"
              disabled={saving}
            >

              {saving && (
                <LoaderCircle
                  size={17}
                  className="spin"
                />
              )}

              {register
                ? "Create account"
                : "Log in"}

              <ArrowRight size={17} />

            </button>

          </form>


          <p className="auth-switch">

            {register
              ? "Already have an account?"
              : "New to Staywise?"}

            {" "}

            <Link
              href={
                register
                  ? "/login"
                  : owner
                  ? "/owner/register"
                  : "/register"
              }
            >
              {register
                ? "Log in"
                : "Create one"}
            </Link>

          </p>


          {!register &&
            !owner && (
              <Link
                href="/owner/register"
                className="owner-link"
              >
                <HousePlus size={14} />

                Want to list a property?
                Register as a host
              </Link>
            )}

        </div>

      </main>

    </Page>
  );
}


// ============================================================
// BOOKING CARD
// ============================================================

function BookingCard({
  booking,
  onCancel,
}) {
  return (
    <article className="booking-row">

      <ImageOrGradient
        src={booking.hotelImage}
        alt={booking.hotelName}
      />


      <div className="booking-copy">

        <div>

          <span
            className={`status ${booking.bookingStatus}`}
          >
            {booking.bookingStatus.replace(
              "_",
              " "
            )}
          </span>

          <span className="muted">
            {booking.paymentStatus}
          </span>

        </div>


        <h3>
          {booking.hotelName}
        </h3>

        <p>
          {booking.roomName}
          {" · "}
          {dateText(
            booking.checkIn
          )}
          {" — "}
          {dateText(
            booking.checkOut
          )}
        </p>

        <small>
          Booking{" "}
          {booking.id
            .slice(0, 8)
            .toUpperCase()}
        </small>

      </div>


      <div className="booking-end">

        <strong>
          {money.format(
            booking.totalAmount
          )}
        </strong>


        <div>

          <Link
            href={`/booking/${booking.id}`}
            className="button outline small"
          >
            Details
          </Link>


          {onCancel && (
            <button
              className="button danger small"
              onClick={onCancel}
            >
              Cancel
            </button>
          )}

        </div>

      </div>

    </article>
  );
}


// ============================================================
// GUEST DASHBOARD
// ============================================================

function GuestDashboard() {
  const result =
    useResource(
      api.bookings,
      []
    );

  const bookings =
    result.data || [];

  const upcoming =
    bookings.filter(
      (item) =>
        item.bookingStatus !==
          "cancelled" &&
        new Date(
          item.checkOut
        ) >= new Date()
    );


  const handleCancel =
    async (booking) => {

      const total =
        Number(
          booking.totalAmount || 0
        );

      const fee =
        total * 0.15;

      const refund =
        total - fee;

      const confirmed =
        window.confirm(
          `Are you sure you want to cancel this booking?\n\n` +
          `Total paid: ${money.format(total)}\n` +
          `Cancellation charge (15%): ${money.format(fee)}\n` +
          `Refund (85%): ${money.format(refund)}\n\n` +
          `The remaining 85% will be submitted for refund.`
        );

      if (!confirmed) {
        return;
      }

      try {
        await api.cancel(
          booking.id
        );

        window.location.reload();
      } catch (err) {
        window.alert(
          err.message
        );
      }
    };


  return (
    <Page>

      <main className="container content">

        <div className="dashboard-heading">

          <div>

            <p className="eyebrow">
              Your corner
            </p>

            <h1>
              Your stays.
            </h1>

            <p className="muted">
              Your trips, all in one place.
            </p>

          </div>


          <Link
            href="/hotels"
            className="button primary"
          >
            <Search size={16} />
            Find a stay
          </Link>

        </div>


        <section className="dashboard-section">

          <div className="section-heading">

            <h2>
              Upcoming stays
            </h2>

            <span className="pill accent-pill">
              {upcoming.length} planned
            </span>

          </div>


          {result.loading ? (
            <Skeletons />
          ) : result.error ? (
            <Empty
              title="Sign in to see your bookings"
              text={
                result.error.message
              }
              action="Log in"
              href="/login"
            />
          ) : upcoming.length ? (
            upcoming.map(
              (booking) => (
                <BookingCard
                  key={booking.id}
                  booking={booking}
                  onCancel={() =>
                    handleCancel(
                      booking
                    )
                  }
                />
              )
            )
          ) : (
            <Empty
              title="No plans on the calendar"
              text="The best kind of trip is the one you haven’t booked yet."
              action="Browse stays"
            />
          )}

        </section>


        <section className="dashboard-section">

          <h2>
            Past stays
          </h2>


          {bookings
            .filter(
              (item) =>
                !upcoming.includes(
                  item
                )
            )
            .map(
              (booking) => (
                <BookingCard
                  key={booking.id}
                  booking={booking}
                />
              )
            )}

        </section>

      </main>

    </Page>
  );
}


// ============================================================
// BOOKING DETAIL
// ============================================================

function BookingDetail() {
  const { bookingId } =
    useParams();

  const result =
    useResource(
      api.bookings,
      []
    );

  const [busy, setBusy] =
    useState(false);

  const [payError, setPayError] =
    useState("");


  const booking =
    result.data?.find(
      (item) =>
        item.id === bookingId
    );


  if (result.loading) {
    return (
      <Page>
        <main className="container content">
          <Skeletons />
        </main>
      </Page>
    );
  }


  if (!booking) {
    return (
      <Page>
        <main className="container content">

          <Empty
            title="We can’t find that booking"
            text="It may belong to another account or the link may have expired."
            action="Back to your stays"
            href="/dashboard"
          />

        </main>
      </Page>
    );
  }


  // ==========================================================
  // PAYMENT
  // ==========================================================

  const pay = async () => {

    setBusy(true);
    setPayError("");

    try {

      const order =
        await api.createOrder(
          bookingId
        );


      if (!window.Razorpay) {
        throw new Error(
          "Payment couldn’t load. Check your connection and try again."
        );
      }


      const checkout =
        new window.Razorpay({
          key: order.keyId,
          amount: order.amount,
          currency:
            order.currency,
          order_id:
            order.orderId,

          name: "Staywise",

          description:
            `${order.hotelName} · ${booking.roomName}`,

          prefill: {
            name:
              order.guestName,
            email:
              order.guestEmail,
            contact:
              order.guestPhone,
          },

          theme: {
            color: "#16794b",
          },


          handler:
            async (
              response
            ) => {

              try {

                await api.verifyPayment(
                  bookingId,
                  {
                    razorpay_order_id:
                      response.razorpay_order_id,

                    razorpay_payment_id:
                      response.razorpay_payment_id,

                    razorpay_signature:
                      response.razorpay_signature,
                  }
                );

                window.location.reload();

              } catch (err) {

                setPayError(
                  err.message
                );

                setBusy(false);
              }
            },


          modal: {
            ondismiss: () =>
              setBusy(false),
          },
        });


      checkout.on(
        "payment.failed",
        (response) => {

          setPayError(
            response.error
              ?.description ||
              "Payment failed. Please try again."
          );

          setBusy(false);
        }
      );


      checkout.open();

    } catch (err) {

      setPayError(
        err.message
      );

      setBusy(false);
    }
  };


  // ==========================================================
  // CANCEL
  // ==========================================================

  const cancel =
    async () => {

      const total =
        Number(
          booking.totalAmount || 0
        );

      const feePercent =
        Number(
          booking.refundPolicyPercent ??
            15
        );

      const refundPercent =
        Number(
          booking.refundPercent ??
            (100 - feePercent)
        );

      const cancellationFee =
        Number(
          booking.refundFeeAmount ??
            (
              total *
              feePercent /
              100
            )
        );

      const refundAmount =
        Number(
          booking.refundAmount ??
            (
              total -
              cancellationFee
            )
        );


      const confirmed =
        window.confirm(
          `Are you sure you want to cancel this booking?\n\n` +
          `Total amount paid: ${money.format(total)}\n` +
          `Cancellation charge (${feePercent}%): ${money.format(cancellationFee)}\n` +
          `Refund (${refundPercent}%): ${money.format(refundAmount)}\n\n` +
          `Click OK to cancel and submit the refund.`
        );


      if (!confirmed) {
        return;
      }


      setBusy(true);
      setPayError("");


      try {

        await api.cancel(
          bookingId
        );

        window.location.reload();

      } catch (err) {

        setPayError(
          err.message
        );

        setBusy(false);
      }
    };


  const isCancelled =
    booking.bookingStatus ===
    "cancelled";

  const isRefunded =
    booking.paymentStatus ===
      "refunded" ||
    booking.refundStatus ===
      "processed";


  return (
    <Page>

      <main className="container content narrow">

        <Link
          href="/dashboard"
          className="text-link back-link"
        >
          <ChevronLeft size={16} />
          Your stays
        </Link>


        {/* =====================================================
            BOOKING HEADER
        ===================================================== */}

        <div className="confirmation">

          <ImageOrGradient
            src={booking.hotelImage}
            alt={booking.hotelName}
          />


          <div>

            <span className="eyebrow accent">

              <CircleCheck size={18} />

              {isCancelled
                ? "Cancelled"
                : booking.paymentStatus ===
                  "paid"
                ? "You’re all set"
                : "Booking created"}

            </span>


            <h1>
              {booking.hotelName}
            </h1>

            <p>
              {booking.roomName}
            </p>

            <small>
              Confirmation{" "}
              {booking.id.toUpperCase()}
            </small>

          </div>


          <div className="confirmation-details">

            <Info
              label="Check in"
              value={dateText(
                booking.checkIn
              )}
            />

            <Info
              label="Check out"
              value={dateText(
                booking.checkOut
              )}
            />

            <Info
              label="Guests"
              value={`${booking.guests} guests`}
            />

            <Info
              label="Total"
              value={money.format(
                booking.totalAmount
              )}
            />

          </div>

        </div>


        {/* =====================================================
            NEXT STEPS
        ===================================================== */}

        <div className="next-steps">

          <div>

            {isCancelled ? (
              <>

                <h2>
                  Booking cancelled
                </h2>


                {isRefunded ? (

                  <p>
                    Your booking has
                    been cancelled and
                    the applicable refund
                    has been submitted.
                    A cancellation and
                    refund email has been
                    sent to your email
                    address.
                  </p>

                ) : (

                  <p>
                    This booking was
                    cancelled before
                    payment was completed,
                    so no refund was
                    required.
                  </p>

                )}

              </>
            ) : (
              <>

                <h2>
                  Next steps
                </h2>


                <p>

                  {booking.paymentStatus ===
                  "paid"
                    ? "Your host has your reservation, and a confirmation email is on its way."
                    : "Pay securely with Razorpay (test mode) to confirm your stay."}

                </p>

              </>
            )}


            {payError && (
              <p className="error">

                <CircleAlert size={16} />

                {payError}

              </p>
            )}

          </div>


          <div>

            {!isCancelled &&
              booking.paymentStatus !==
                "paid" && (
                <button
                  className="button primary"
                  disabled={busy}
                  onClick={pay}
                >

                  {busy && (
                    <LoaderCircle
                      size={17}
                      className="spin"
                    />
                  )}

                  Pay & confirm

                </button>
              )}


            {!isCancelled && (
              <button
                className="button danger"
                disabled={busy}
                onClick={cancel}
              >
                {busy && (
                  <LoaderCircle
                    size={17}
                    className="spin"
                  />
                )}

                Cancel booking
              </button>
            )}

          </div>

        </div>


        {/* =====================================================
            REFUND SUMMARY
        ===================================================== */}

        {isCancelled &&
          isRefunded && (
            <section className="refund-summary panel">

              <div className="section-heading">

                <div>

                  <p className="eyebrow accent">
                    Refund completed
                  </p>

                  <h2>
                    Your refund
                  </h2>

                </div>


                <ShieldCheck
                  className="accent-text"
                />

              </div>


              <p className="muted">
                Your booking was
                cancelled and the
                cancellation charge
                was deducted according
                to the Staywise refund
                policy.
              </p>


              <div className="refund-calculation">

                <div>

                  <span>
                    Total amount paid
                  </span>

                  <strong>
                    {money.format(
                      booking.totalAmount
                    )}
                  </strong>

                </div>


                <div>

                  <span>
                    Cancellation charge (
                    {booking.refundPolicyPercent ??
                      15}
                    %)
                  </span>

                  <strong>
                    -{" "}
                    {money.format(
                      booking.refundFeeAmount ||
                        0
                    )}
                  </strong>

                </div>


                <div className="refund-total">

                  <span>
                    Refund (
                    {booking.refundPercent ??
                      85}
                    %)
                  </span>

                  <strong>
                    {money.format(
                      booking.refundAmount ||
                        0
                    )}
                  </strong>

                </div>

              </div>


              <div className="refund-status-box">

                <div className="refund-reference">

                  <span>
                    Refund status
                  </span>

                  <strong>
                    {booking.refundStatus ||
                      "Processed"}
                  </strong>

                </div>


                <div className="refund-reference">

                  <span>
                    Refund reference
                  </span>

                  <strong>
                    {booking.razorpayRefundId ||
                      "—"}
                  </strong>

                </div>

              </div>


              <div className="notice">

                <strong>
                  Refund timing
                </strong>

                <br />

                The refund has been
                submitted through the
                payment provider. Your
                bank or payment provider
                may take additional time
                to show the refunded
                amount in your account.

              </div>

            </section>
          )}

      </main>

    </Page>
  );
}


// ============================================================
// INFO
// ============================================================

function Info({
  label,
  value,
}) {
  return (
    <div>

      <small>
        {label}
      </small>

      <b>
        {value}
      </b>

    </div>
  );
}


// ============================================================
// OWNER SHELL
// ============================================================

function OwnerShell({
  children,
}) {
  return (
    <Page>
      <main className="container content">
        {children}
      </main>
    </Page>
  );
}


// ============================================================
// OWNER METRIC
// ============================================================

function Metric({
  icon,
  label,
  value,
  accent = false,
}) {
  return (
    <div
      className={`metric ${
        accent
          ? "metric-accent"
          : ""
      }`}
    >

      <span>
        {icon}
      </span>

      <small>
        {label}
      </small>

      <strong>
        {value}
      </strong>

    </div>
  );
}


// ============================================================
// OWNER DASHBOARD
// ============================================================

function OwnerDashboard() {
  const dashboard =
    useResource(
      api.ownerDashboard,
      []
    );

  const bookings =
    useResource(
      api.ownerBookings,
      []
    );

  if (dashboard.loading) {
    return (
      <OwnerShell>
        <Skeletons />
      </OwnerShell>
    );
  }


  if (dashboard.error) {
    return (
      <OwnerShell>

        <Empty
          title="Owner access needed"
          text={
            dashboard.error.message
          }
          action="Owner login"
          href="/owner/login"
        />

      </OwnerShell>
    );
  }


  const data =
    dashboard.data;


  return (
    <OwnerShell>

      <div className="dashboard-heading">

        <div>

          <p className="eyebrow">
            Owner overview
          </p>

          <h1>
            Good morning.
          </h1>

          <p className="muted">
            Here’s how your places are doing.
          </p>

        </div>


        <Link
          href="/owner/hotels/new"
          className="button primary"
        >
          <Plus size={17} />
          Add a property
        </Link>

      </div>


      <div className="metrics">

        <Metric
          icon={<HousePlus />}
          label="Properties"
          value={
            data.totalProperties
          }
        />

        <Metric
          icon={<TicketCheck />}
          label="Total bookings"
          value={
            data.totalBookings
          }
        />

        <Metric
          icon={<Clock3 />}
          label="Needs attention"
          value={
            data.pendingBookings
          }
          accent
        />

        <Metric
          icon={<WalletCards />}
          label="Revenue"
          value={money.format(
            data.totalRevenue
          )}
        />

      </div>


      <div className="owner-grid">

        <section className="panel">

          <div className="section-heading">

            <h2>
              Bookings over time
            </h2>

            <span className="muted">
              This year
            </span>

          </div>


          <div className="bars">

            {data.monthlyBookings.map(
              (item) => (
                <div
                  key={item.month}
                >

                  <span
                    style={{
                      height: `${Math.max(
                        8,
                        item.bookings *
                          18
                      )}%`,
                    }}
                  />

                  <small>
                    {item.month.slice(
                      0,
                      3
                    )}
                  </small>

                </div>
              )
            )}

          </div>

        </section>


        <section className="pulse-card">

          <p className="eyebrow accent">
            Quick pulse
          </p>

          <h2>
            Your guests are looking.
          </h2>

          <p>
            Confirmed{" "}
            <b>
              {data.confirmedBookings}
            </b>
          </p>

          <p>
            Pending{" "}
            <b>
              {data.pendingBookings}
            </b>
          </p>

          <p>
            Cancelled{" "}
            <b>
              {data.cancelledBookings}
            </b>
          </p>

          <Link
            href="/owner/bookings"
            className="text-link accent-text"
          >
            Review bookings
            <ArrowRight size={16} />
          </Link>

        </section>

      </div>


      <section className="panel latest">

        <div className="section-heading">

          <h2>
            Latest reservations
          </h2>

          <Link
            href="/owner/bookings"
            className="text-link"
          >
            View all
          </Link>

        </div>


        {(bookings.data || [])
          .slice(0, 4)
          .map(
            (booking) => (
              <div
                className="latest-row"
                key={booking.id}
              >

                <span>

                  <b>
                    {booking.guestName}
                  </b>

                  <small>
                    {booking.hotelName}
                    {" · "}
                    {dateText(
                      booking.checkIn
                    )}
                  </small>

                </span>

                <b>
                  {money.format(
                    booking.totalAmount
                  )}
                </b>

              </div>
            )
          )}

      </section>

    </OwnerShell>
  );
}


// ============================================================
// OWNER BOOKINGS
// ============================================================

function OwnerBookings() {
  const result =
    useResource(
      api.ownerBookings,
      []
    );

  const [filter, setFilter] =
    useState("all");

  const shown =
    (result.data || []).filter(
      (item) =>
        filter === "all" ||
        item.bookingStatus ===
          filter
    );


  const update =
    async (
      id,
      status
    ) => {

      await api.updateBooking(
        id,
        status
      );

      window.location.reload();
    };


  return (
    <OwnerShell>

      <div className="dashboard-heading">

        <div>

          <p className="eyebrow">
            Owner workspace
          </p>

          <h1>
            Bookings.
          </h1>

          <p className="muted">
            The people who chose your place.
          </p>

        </div>


        <Link
          href="/owner/dashboard"
          className="text-link"
        >
          <ChevronLeft size={16} />
          Overview
        </Link>

      </div>


      <div className="filter-pills">

        {[
          "all",
          "pending_payment",
          "confirmed",
          "cancelled",
          "completed",
        ].map((item) => (

          <button
            className={
              filter === item
                ? "selected"
                : ""
            }
            key={item}
            onClick={() =>
              setFilter(item)
            }
          >
            {item.replace(
              "_",
              " "
            )}
          </button>

        ))}

      </div>


      {result.loading ? (
        <Skeletons />
      ) : shown.length ? (

        <div className="owner-bookings">

          {shown.map(
            (booking) => (

              <article
                className="owner-booking"
                key={booking.id}
              >

                <ImageOrGradient
                  src={
                    booking.hotelImage
                  }
                  alt={
                    booking.hotelName
                  }
                />


                <div>

                  <b>
                    {booking.guestName}
                  </b>

                  <p>
                    {booking.hotelName}
                    {" · "}
                    {booking.roomName}
                  </p>

                  <small>
                    {dateText(
                      booking.checkIn
                    )}
                    {" — "}
                    {dateText(
                      booking.checkOut
                    )}
                    {" · "}
                    {booking.guests} guests
                  </small>

                </div>


                <div>

                  <strong>
                    {money.format(
                      booking.totalAmount
                    )}
                  </strong>


                  {booking.bookingStatus ===
                    "pending_payment" && (
                    <div>

                      <button
                        className="button secondary small"
                        onClick={() =>
                          update(
                            booking.id,
                            "confirmed"
                          )
                        }
                      >
                        Confirm
                      </button>

                      <button
                        className="button outline small"
                        onClick={() =>
                          update(
                            booking.id,
                            "rejected"
                          )
                        }
                      >
                        Decline
                      </button>

                    </div>
                  )}


                  {booking.bookingStatus ===
                    "confirmed" && (
                    <button
                      className="button outline small"
                      onClick={() =>
                        update(
                          booking.id,
                          "completed"
                        )
                      }
                    >
                      Mark complete
                    </button>
                  )}

                </div>

              </article>
            )
          )}

        </div>

      ) : (

        <Empty
          title="A quiet check-in"
          text="New reservations will show up here as soon as guests book."
        />

      )}

    </OwnerShell>
  );
}


// ============================================================
// NEW HOTEL
// ============================================================

function NewHotel() {
  const [, navigate] =
    useLocation();

  const [hotel, setHotel] =
    useState({
      name: "",
      propertyType:
        "Boutique hotel",
      description: "",
      city: "",
      country: "",
      address: "",
      image: "",
      amenities:
        "Wi-Fi, Breakfast, Air conditioning",
    });

  const [room, setRoom] =
    useState({
      name:
        "The signature room",
      type: "Double",
      description:
        "A calm, comfortable room for slow mornings.",
      maxGuests: "2",
      beds: "1",
      pricePerNight: "180",
      totalRooms: "2",
      amenities:
        "Wi-Fi, Private bathroom",
      image: "",
    });

  const [error, setError] =
    useState("");

  const [saving, setSaving] =
    useState(false);


  const submit =
    async (event) => {

      event.preventDefault();

      setSaving(true);
      setError("");

      try {

        const created =
          await api.createHotel({
            ...hotel,
            amenities:
              hotel.amenities
                .split(",")
                .map(
                  (item) =>
                    item.trim()
                ),
          });


        await api.createRoom(
          created.id,
          {
            ...room,

            maxGuests:
              Number(
                room.maxGuests
              ),

            beds:
              Number(
                room.beds
              ),

            pricePerNight:
              Number(
                room.pricePerNight
              ),

            totalRooms:
              Number(
                room.totalRooms
              ),

            amenities:
              room.amenities
                .split(",")
                .map(
                  (item) =>
                    item.trim()
                ),
          }
        );


        navigate(
          "/owner/dashboard"
        );

      } catch (err) {

        setError(
          err.message
        );

      } finally {

        setSaving(false);

      }
    };


  const set = (
    key,
    value
  ) =>
    setHotel({
      ...hotel,
      [key]: value,
    });


  const setRoomValue = (
    key,
    value
  ) =>
    setRoom({
      ...room,
      [key]: value,
    });


  return (
    <OwnerShell>

      <Link
        href="/owner/dashboard"
        className="text-link back-link"
      >
        <ChevronLeft size={16} />
        Overview
      </Link>


      <div className="new-property">

        <p className="eyebrow">
          New property
        </p>

        <h1>
          Give it a good beginning.
        </h1>

        <p className="muted">
          Start with the details
          guests need to picture
          themselves there.
        </p>


        <form onSubmit={submit}>

          <section className="panel">

            <h2>
              The basics
            </h2>


            <div className="form-grid two">

              <Field
                label="Property name"
                value={hotel.name}
                onChange={(value) =>
                  set(
                    "name",
                    value
                  )
                }
                placeholder="A name with character"
              />

              <Field
                label="Property type"
                value={
                  hotel.propertyType
                }
                onChange={(value) =>
                  set(
                    "propertyType",
                    value
                  )
                }
                placeholder="Boutique hotel"
              />

              <Field
                label="City"
                value={hotel.city}
                onChange={(value) =>
                  set(
                    "city",
                    value
                  )
                }
                placeholder="Portland"
              />

              <Field
                label="Country"
                value={hotel.country}
                onChange={(value) =>
                  set(
                    "country",
                    value
                  )
                }
                placeholder="United States"
              />

              <Field
                label="Address"
                value={hotel.address}
                onChange={(value) =>
                  set(
                    "address",
                    value
                  )
                }
                placeholder="Street and number"
              />

              <Field
                label="Cover image URL"
                value={hotel.image}
                onChange={(value) =>
                  set(
                    "image",
                    value
                  )
                }
                placeholder="https://…"
              />


              <label className="field full-field">

                <span>
                  Description
                </span>

                <textarea
                  required
                  minLength="20"
                  value={
                    hotel.description
                  }
                  onChange={(e) =>
                    set(
                      "description",
                      e.target.value
                    )
                  }
                />

              </label>


              <Field
                label="Amenities, comma separated"
                value={
                  hotel.amenities
                }
                onChange={(value) =>
                  set(
                    "amenities",
                    value
                  )
                }
                placeholder="Wi-Fi, Breakfast"
              />

            </div>

          </section>


          <section className="panel">

            <div className="row">

              <div>

                <h2>
                  Add your first room
                </h2>

                <p className="muted">
                  Guests need at least
                  one way to stay.
                </p>

              </div>

              <BedDouble className="accent-text" />

            </div>


            <div className="form-grid two">

              <Field
                label="Room name"
                value={room.name}
                onChange={(value) =>
                  setRoomValue(
                    "name",
                    value
                  )
                }
                placeholder="The garden room"
              />

              <Field
                label="Room type"
                value={room.type}
                onChange={(value) =>
                  setRoomValue(
                    "type",
                    value
                  )
                }
                placeholder="Double"
              />

              <Field
                label="Price per night"
                type="number"
                value={
                  room.pricePerNight
                }
                onChange={(value) =>
                  setRoomValue(
                    "pricePerNight",
                    value
                  )
                }
              />

              <Field
                label="Total rooms"
                type="number"
                value={
                  room.totalRooms
                }
                onChange={(value) =>
                  setRoomValue(
                    "totalRooms",
                    value
                  )
                }
              />

              <Field
                label="Max guests"
                type="number"
                value={
                  room.maxGuests
                }
                onChange={(value) =>
                  setRoomValue(
                    "maxGuests",
                    value
                  )
                }
              />

              <Field
                label="Beds"
                type="number"
                value={room.beds}
                onChange={(value) =>
                  setRoomValue(
                    "beds",
                    value
                  )
                }
              />

            </div>

          </section>


          {error && (
            <p className="error">
              {error}
            </p>
          )}


          <button
            className="button primary"
            disabled={saving}
          >

            {saving && (
              <LoaderCircle
                size={17}
                className="spin"
              />
            )}

            Publish property

            <ArrowRight size={17} />

          </button>

        </form>

      </div>

    </OwnerShell>
  );
}


// ============================================================
// REFUND POLICY PAGE
// ============================================================

function RefundPolicyPage() {
  const policy =
    useResource(
      api.refundPolicy,
      []
    );


  const feePercent =
    Number(
      policy.data
        ?.cancellationFeePercent ??
        15
    );


  const refundPercent =
    Number(
      policy.data?.refundPercent ??
        85
    );


  // Example amount
  const exampleTotal = 10000;

  const exampleFee =
    (
      exampleTotal *
      feePercent /
      100
    );

  const exampleRefund =
    (
      exampleTotal -
      exampleFee
    );


  return (
    <Page>

      <main className="container content narrow">

        <Link
          href="/"
          className="text-link back-link"
        >
          <ChevronLeft size={16} />
          Back home
        </Link>


        <div className="refund-policy-page">


          {/* =================================================
              HEADER
          ================================================= */}

          <div className="refund-policy-header">

            <div className="refund-policy-icon">

              <ShieldCheck size={30} />

            </div>


            <p className="eyebrow">
              Staywise policy
            </p>


            <h1>
              Refund & cancellation policy.
            </h1>


            <p className="muted">

              We keep the calculation
              simple and transparent.

              If a guest cancels a
              paid booking,

              {" "}
              <strong>
                {feePercent}%
              </strong>

              {" "}
              is retained as the
              cancellation charge and

              {" "}
              <strong>
                {refundPercent}%
              </strong>

              {" "}
              is refunded.

            </p>

          </div>


          {/* =================================================
              POLICY CARDS
          ================================================= */}

          <section className="refund-policy-card">


            <div className="refund-policy-rule">

              <div>

                <span className="policy-number">
                  {feePercent}%
                </span>

                <h3>
                  Cancellation charge
                </h3>

                <p>
                  This amount is
                  retained from the
                  total amount paid when
                  a guest cancels a paid
                  booking.
                </p>

              </div>

            </div>


            <div className="refund-policy-rule refund-highlight">

              <div>

                <span className="policy-number">
                  {refundPercent}%
                </span>

                <h3>
                  Refund to guest
                </h3>

                <p>
                  The remaining amount
                  is submitted to Razorpay
                  for refund to the original
                  payment method.
                </p>

              </div>

            </div>

          </section>


          {/* =================================================
              EXAMPLE
          ================================================= */}

          <section className="refund-example panel">

            <p className="eyebrow accent">
              Example
            </p>


            <h2>
              If you paid{" "}
              {money.format(
                exampleTotal
              )}
            </h2>


            <div className="refund-calculation">

              <div>

                <span>
                  Total paid
                </span>

                <strong>
                  {money.format(
                    exampleTotal
                  )}
                </strong>

              </div>


              <div>

                <span>
                  Cancellation charge (
                  {feePercent}%)
                </span>

                <strong>
                  -{" "}
                  {money.format(
                    exampleFee
                  )}
                </strong>

              </div>


              <div className="refund-total">

                <span>
                  Refund (
                  {refundPercent}%)
                </span>

                <strong>
                  {money.format(
                    exampleRefund
                  )}
                </strong>

              </div>

            </div>

          </section>


          {/* =================================================
              CALCULATION FORMULA
          ================================================= */}

          <section className="refund-formula panel">

            <p className="eyebrow accent">
              Formula
            </p>

            <h2>
              How the refund is calculated
            </h2>


            <div className="formula-box">

              <code>
                Cancellation charge =
                Total paid × {feePercent}%
              </code>

              <code>
                Refund =
                Total paid × {refundPercent}%
              </code>

            </div>

          </section>


          {/* =================================================
              HOW IT WORKS
          ================================================= */}

          <section className="refund-policy-info">

            <h2>
              How cancellation works
            </h2>


            <ol>

              <li>
                The guest opens their
                booking.
              </li>


              <li>
                The guest selects
                <strong>
                  {" "}Cancel booking
                </strong>.
              </li>


              <li>
                Staywise calculates
                the{" "}
                <strong>
                  {feePercent}%
                </strong>{" "}
                cancellation charge.
              </li>


              <li>
                Staywise calculates the
                remaining{" "}
                <strong>
                  {refundPercent}%
                </strong>{" "}
                refund amount.
              </li>


              <li>
                The refund is submitted
                to Razorpay.
              </li>


              <li>
                The booking is marked
                as cancelled.
              </li>


              <li>
                The guest receives an
                email containing the
                complete calculation,
                refund amount and refund
                reference.
              </li>

            </ol>

          </section>


          {/* =================================================
              IMPORTANT INFORMATION
          ================================================= */}

          <div className="notice">

            <strong>
              Refund timing
            </strong>

            <br />

            Once the refund has been
            successfully created, the
            payment provider and bank
            may require additional
            processing time before the
            money appears in the guest's
            account.

          </div>


          <div className="notice refund-policy-notice">

            <strong>
              Please note
            </strong>

            <br />

            The cancellation charge is
            calculated from the total
            amount actually paid for the
            booking. The refund is sent
            back through the payment
            provider to the original
            payment method.

          </div>

        </div>

      </main>

    </Page>
  );
}


// ============================================================
// ROUTES
// ============================================================

function AppRoutes() {
  return (
    <Switch>

      <Route
        path="/"
        component={HomePage}
      />

      <Route
        path="/hotels"
        component={HotelsPage}
      />

      <Route
        path="/hotels/:hotelId"
        component={HotelDetailsPage}
      />

      <Route
        path="/login"
        component={() => (
          <AuthPage />
        )}
      />

      <Route
        path="/register"
        component={() => (
          <AuthPage register />
        )}
      />

      <Route
        path="/owner/register"
        component={() => (
          <AuthPage
            owner
            register
          />
        )}
      />

      <Route
        path="/dashboard"
        component={GuestDashboard}
      />

      <Route
        path="/booking/:bookingId"
        component={BookingDetail}
      />

      <Route
        path="/refund-policy"
        component={RefundPolicyPage}
      />

      <Route
        path="/owner/dashboard"
        component={OwnerDashboard}
      />

      <Route
        path="/owner/bookings"
        component={OwnerBookings}
      />

      <Route
        path="/owner/hotels/new"
        component={NewHotel}
      />

      <Route>

        <Empty
          title="Page not found"
          text="That page wandered off."
          action="Back home"
          href="/"
        />

      </Route>

    </Switch>
  );
}


// ============================================================
// APP
// ============================================================

export default function App() {
  return (
    <WouterRouter>
      <AppRoutes />
    </WouterRouter>
  );
}