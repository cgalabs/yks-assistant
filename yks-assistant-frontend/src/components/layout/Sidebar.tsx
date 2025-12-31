import { NavLink, useLocation, Link } from "react-router-dom";
import { Camera, Sparkles, Target, Clock, Gauge, User } from "lucide-react";
import { cn } from "@/lib/utils";
import logo from "@/assets/logo.png";

const navItems = [
  { to: "/solve", icon: Camera, label: "Çöz" },
  { to: "/generate", icon: Sparkles, label: "Üret" },
  { to: "/measure", icon: Gauge, label: "Ölç" },
  { to: "/coach", icon: Target, label: "Koç" },
  { to: "/history", icon: Clock, label: "Geçmiş" },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 glass border-r border-border/50 z-50 flex flex-col">
      {/* Logo Section */}
      <div className="p-6">
        <Link to="/" className="flex items-center gap-2">
          <img src={logo} alt="YKS Asistan" className="h-10 w-auto" />
        </Link>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-4 space-y-2 mt-4">
        {navItems.map((item) => {
          const isActive = location.pathname === item.to ||
            (item.to === "/solve" && location.pathname === "/");

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                isActive
                  ? "text-primary bg-primary/10"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              )}
            >
              <div
                className={cn(
                  "p-2 rounded-lg transition-all duration-200",
                  isActive ? "gradient-primary shadow-glow text-primary-foreground" : "group-hover:text-primary"
                )}
              >
                <item.icon className="w-5 h-5" />
              </div>
              <span className="font-medium">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Profile Section at Bottom */}
      <div className="p-4 border-t border-border/50">
        <Link
          to="/profile"
          className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-secondary/50 transition-all duration-200 group"
        >
          <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center text-primary-foreground shadow-md">
            <User className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-foreground">Profilim</span>
            <span className="text-[10px] text-muted-foreground group-hover:text-primary transition-colors">Ayarlar ve Başarılar</span>
          </div>
        </Link>
      </div>
    </aside>
  );
}
