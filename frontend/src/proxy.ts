import { NextResponse, type NextRequest } from "next/server";
import { adminAuthCookie, getAdminSessionToken } from "@/lib/adminAuth";

export function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const token = getAdminSessionToken();
  const isAuthenticated = Boolean(token && request.cookies.get(adminAuthCookie)?.value === token);
  const isLoginPage = pathname.startsWith("/admin/login");

  if (isLoginPage) {
    if (isAuthenticated) {
      return NextResponse.redirect(new URL("/admin", request.url));
    }
    return NextResponse.next();
  }

  if (!isAuthenticated) {
    const loginUrl = new URL("/admin/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"],
};

