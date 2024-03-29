# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

from luxon.core.constants import HTTP_STATUS_CODES

class Error(Exception):
    """Tachyonic Root Exception

    Args:
        message (str): Error Message.
    """
    def __init__(self, message):
        self._msg = message
        super().__init__(self._msg)

    def __str__(self):
        return str(self._msg)

class NoContextError(Error):
    """No Context Error.

    This error is raised when an operation is performed outside of the required
    environment/context.

    Args:
        message (str): Reason for context error.
    """
    def __init__(self, message):
        super().__init__(message)

class ValidationError(Error):
    """Validation Error.

    During a process it was unable to validate information with the context of
    the request. Message arguement may contain a detailed response.

    Args:
        message (str): Reason for validation error.
    """
    def __init__(self, message):
        super().__init__(message)

class AccessDenied(ValidationError):
    """Access Denied.

    This error indicates that the server understood the request but refuses to
    authorize it.  A server that wishes to make public why the request has been
    forbidden can describe that reason using message arguement.

    If authentication credentials were provided in the request, the server
    considers them insufficient to grant access.  The client SHOULD NOT
    automatically repeat the request with the same credentials.

    Args:
        message (str): Reason for access denied.
    """
    def __init__(self, message):
        super().__init__(message)

class NotFound(ValidationError):
    """Not Found.

    This error indicates when a specific resource is not found. The message
    arguement can be used to describe what has not been found.

    Args:
        message (str): Representation of resource not found.
    """
    def __init__(self, message):
        super().__init__( message)

class FieldInvalid(ValidationError):
    """Field Invalid.

    The value of the specified field is invalid. Typically used by models.

    Args:
        field (str): The actual field id/descriptor.
        label (str): User friendly field title/name.
        description (str): Field Description.
        value (str): Field value used.
    """
    def __init__(self, field, label, description, value):
        self.field = field
        self.label = label
        self.description = description
        self.value = value
        msg = "The field '%s' (%s) has invalid value of %s. (%s)" % (label,
                                                                  field,
                                                                  value,
                                                                  description,)
        super().__init__(msg)

class FieldMissing(ValidationError):
    """Field Missing.

    The value of the specified field is missing. Typically used by models.

    Args:
        field (str): The actual field id/descriptor.
        label (str): User friendly field title/name.
        description (str): Field Description.
    """
    def __init__(self, field, label, description):
        self.field = field
        self.label = label
        self.description = description
        msg = "The field '%s' (%s) is not defined. (%s)" % (label,
                                                            field,
                                                            description,)
        super().__init__(msg)

class MultipleOblectsReturned(ValidationError):
    """Multiple Objects Returned.

    This error is raised when multiple objects are returned when expecting one.

    Args:
        message (str): Reason for error.
    """
    def __init__(self, message):
        super().__init__(message)

class RestClientError(Error):
    """Raw Rest Client Error.

    Args:
        message (str): Reason for error.
    """
    def __init__(self, message):
        super().__init__(message)

class ClientError(RestClientError):
    """Tachyonic API Client Error.

    Args:
        message (str): Reason for error.
    """
    def __init__(self, message):
        super().__init__(message)

class PoolExhausted(Error):
    """Pool Exhausted Error.

    Exception that is raised when attempting to
    create/retrieve a connector object from a pool
    after the pool limit has been reached.

    Args:
        pool_name (str): Identity of pool.
        max_size (str): Overflow + Pool Size Limit.
    """
    def __init__(self, pool_name, max_size):
        description = "%s pool reached size %s" % (pool_name, max_size)
        super().__init__(description)

class HTTPError(Error):
    """Base HTTP Error.

    All other HTTP errors use this as the base class.

    Keyword Args:
        status (int): HTTP Status code.
        description (str): Human friendly description of the error.
        title (str): Error title (default '400 Bad Request')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    __slots__ = ('status', 'href', 'title', 'description', 'headers')

    def __init__(self, status=500, description=None, title=None,
                 headers={}, href=None):
        self.status = status
        self.href = href

        if title is None:
            self.title = "%s %s" % (self.status, HTTP_STATUS_CODES[self.status])

        if description is None:
            self.description = ': ' + description
        else:
            self.description = ''

        self.headers = headers

        super().__init__(self.title + self.description)

class HTTPBadRequest(HTTPError):
    """400 Bad Request.

    The 400 Bad Request indicates that the server cannot or will not process
    the request due to something that is perceived to be a client error (e.g.,
    malformed request syntax, invalid request message framing, or deceptive
    request routing).

    Reference RFC 7231, Section 6.5.1

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '400 Bad Request')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(400, **kwargs)

class HTTPUnauthorized(HTTPError):
    """401 Unauthorized.

    This 401 Unauthorized indicates that the request has not been applied
    because it lacks valid authentication credentials for the target resource.
    The server generating a 401 response MUST send a WWW-Authenticate header
    field (RFC 7231, Section 4.1) containing at least one challenge applicable
    to the target resource.

    If the request included authentication credentials, then the 401 response
    indicates that authorization has been refused for those response indicates
    that authorization has been refused for those credentials.  The user agent
    MAY repeat the request with a new or replaced Authorization header field
    (RFC 7231, Section 4.2).  If the 401 response contains the same challenge as
    the prior response, and the user agent has already attempted authentication
    at least once, then the user agent SHOULD present the enclosed
    representation to the user, since it usually contains relevant diagnostic
    information.

    Reference RFC 7235, Section 3.1

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '401 Unauthorized')
        challenges (dict): A dict of one or more authentication challenges to
            use as the value of WWW-Authenticate header in response.
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """

    def __init__(self, description=None, title=None, challenges=None,
                 headers={}, **kwargs):
        if challenges is not None:
            headers['WWW-Authenticate'] = ', '.join(challenges)
        super().__init__(401, description, title, headers)

class HTTPPaymentRequired(HTTPError):
    """402 Payment Required.

    The 402 Payment Required status code is reserved for future use.

    Reference RFC 7231, Section 6.5.2

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '402 Payment Required')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """

    def __init__(self, **kwargs):
        super().__init__(402, **kwargs)

class HTTPForbidden(HTTPError):
    """403 Forbidden.

    The 403 (Forbidden) status code indicates that the server understood
    the request but refuses to authorize it.  A server that wishes to
    make public why the request has been forbidden can describe that
    reason in the response payload (if any).

    If authentication credentials were provided in the request, the
    server considers them insufficient to grant access.  The client
    SHOULD NOT automatically repeat the request with the same
    credentials.  The client MAY repeat the request with new or different
    credentials.  However, a request might be forbidden for reasons
    unrelated to the credentials.

    An origin server that wishes to "hide" the current existence of a
    forbidden target resource MAY instead respond with a status code of
    404 (Not Found).

    Reference RFC 7231, Section 6.5.3

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '403 Forbidden')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(403, **kwargs)

class HTTPNotFound(HTTPError):
    """404 Not Found.

    The 404 (Not Found) status code indicates that the origin server did
    not find a current representation for the target resource or is not
    willing to disclose that one exists.  A 404 status code does not
    indicate whether this lack of representation is temporary or
    permanent; the 410 (Gone) status code is preferred over 404 if the
    origin server knows, presumably through some configurable means, that
    the condition is likely to be permanent.

    A 404 response is cacheable by default; i.e., unless otherwise
    indicated by the method definition or explicit cache controls (see
    Section 4.2.2 of RFC7234).

    Reference RFC 7231, Section 6.5.4

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '404 Not Found')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(404, **kwargs)

class HTTPMethodNotAllowed(HTTPError):
    """405 Method Not Allowed.

    The 405 (Method Not Allowed) status code indicates that the method
    received in the request-line is known by the origin server but not
    supported by the target resource.  The origin server MUST generate an
    Allow header field in a 405 response containing a list of the target
    resource's currently supported methods.

    A 405 response is cacheable by default; i.e., unless otherwise
    indicated by the method definition or explicit cache controls (see
    Section 4.2.2 of RFC7234).

    Reference RFC 7231, Section 6.5.5

    Keyword Args:
        allowed_methods (list of str): Allowed HTTP methods for this resource.
            e.g. ['GET', 'POST',]
        description (str): Human friendly description of the error.
        title (str): Error title (default '405 Method Not Allowed')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, allowed_methods=[], description=None, title=None,
                 headers={}, **kwargs):
        headers['Allow'] = ', '.join(allowed_methods)
        super().__init__(405, description, title, headers, **kwargs)

class HTTPNotAcceptable(HTTPError):
    """406 Not Acceptable.

    The 406 Not Acceptable status code indicates that the target
    resource does not have a current representation that would be
    acceptable to the user agent, according to the proactive negotiation
    header fields received in the request (RFC7234, Section 5.3), and the
    server is unwilling to supply a default representation.

    The server SHOULD generate a payload containing a list of available
    representation characteristics and corresponding resource identifiers
    from which the user or user agent can choose the one most
    appropriate.  A user agent MAY automatically select the most
    appropriate choice from that list.  However, this specification does
    not define any standard for such automatic selection, as described in
    Section 6.4.1.

    Reference RFC 7231, Section 6.5.6

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '405 Method Not Allowed')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(406, **kwargs)


class HTTPConflict(HTTPError):
    """409 Conflict.

    The 409 Conflict status code indicates that the request could not
    be completed due to a conflict with the current state of the target
    resource.  This code is used in situations where the user might be
    able to resolve the conflict and resubmit the request.  The server
    SHOULD generate a payload that includes enough information for a user
    to recognize the source of the conflict.

    Conflicts are most likely to occur in response to a PUT request.  For
    example, if versioning were being used and the representation being
    PUT included changes to a resource that conflict with those made by
    an earlier (third-party) request, the origin server might use a 409
    response to indicate that it can't complete the request.  In this
    case, the response representation would likely contain information
    useful for merging the differences based on the revision history.

    Reference RFC 7231, Section 6.5.8

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '409 Conflict')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(409, **kwargs)

class HTTPGone(HTTPError):
    """410 Gone.

    The 410 Gone status code indicates that access to the target
    resource is no longer available at the origin server and that this
    condition is likely to be permanent.  If the origin server does not
    know, or has no facility to determine, whether or not the condition
    is permanent, the status code 404 (Not Found) ought to be used
    instead.

    The 410 response is primarily intended to assist the task of web
    maintenance by notifying the recipient that the resource is
    intentionally unavailable and that the server owners desire that
    remote links to that resource be removed.  Such an event is common
    for limited-time, promotional services and for resources belonging to
    individuals no longer associated with the origin server's site.  It
    is not necessary to mark all permanently unavailable resources as
    "gone" or to keep the mark for any length of time -- that is left to
    the discretion of the server owner.

    A 410 response is cacheable by default; i.e., unless otherwise
    indicated by the method definition or explicit cache controls (see
    Section 4.2.2 of RFC7234).

    Reference RFC 7231, Section 6.5.9

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '410 Gone')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(410, **kwargs)

class HTTPLengthRequired(HTTPError):
    """411 Length Required.

    The 411 Length Required status code indicates that the server
    refuses to accept the request without a defined Content-Length
    (Section 3.3.2 of RFC7230).  The client MAY repeat the request if
    it adds a valid Content-Length header field containing the length of
    the message body in the request message.

    Reference RFC 7231, Section 6.5.10

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '411 Length Required')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, description='Content-Length header required from client.', **kwargs):
        super().__init__(411, description, **kwargs)

class HTTPPreconditionFailed(HTTPError):
    """412 Precondition Failed.

    The 412 Precondition Failed status code indicates that one or more
    conditions given in the request header fields evaluated to false when
    tested on the server.  This response code allows the client to place
    preconditions on the current resource state (its current
    representations and metadata) and, thus, prevent the request method
    from being applied if the target resource is in an unexpected state.

    Reference RFC 7232, Section 4.2

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '412 Precondition Failed')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(412, **kwargs)

class HTTPPayloadTooLarge(HTTPError):
    """413 Payload Too Large.

    The 413 Payload Too Large status code indicates that the server is
    refusing to process a request because the request payload is larger
    than the server is willing or able to process.  The server MAY close
    the connection to prevent the client from continuing the request.

    If the condition is temporary, the server SHOULD generate a
    Retry-After header field to indicate that it is temporary and after
    what time the client MAY try again.

    Reference RFC 7231, Section 6.5.11

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '413 Payload Too Large')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(413, **kwargs)

class HTTPUriTooLong(HTTPError):
    """414 URI Too Long.

    The 414 URI Too Long status code indicates that the server is
    refusing to service the request because the request-target (Section
    5.3 of RFC7230) is longer than the server is willing to interpret.
    This rare condition is only likely to occur when a client has
    improperly converted a POST request to a GET request with long query
    information, when the client has descended into a "black hole" of
    redirection (e.g., a redirected URI prefix that points to a suffix of
    itself) or when the server is under attack by a client attempting to
    exploit potential security holes.

    Reference RFC 7231, Section 6.5.12

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '414 URI Too Long')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(414, **kwargs)

class HTTPUnsupportedMediaType(HTTPError):
    """415 Unsupported Media Type.

    The 415 (Unsupported Media Type) status code indicates that the
    origin server is refusing to service the request because the payload
    is in a format not supported by this method on the target resource.
    The format problem might be due to the request's indicated
    Content-Type or Content-Encoding, or as a result of inspecting the
    data directly.

    Reference RFC 7231, Section 6.5.13

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '415 Unsupported Media Type.')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(415, **kwargs)

class HTTPRangeNotSatisfiable(HTTPError):
    """416 Range Not Satisfiable.

    The 416 (Range Not Satisfiable) status code indicates that none of
    the ranges in the request's Range header field (Section 3.1) overlap
    the current extent of the selected resource or that the set of ranges
    requested has been rejected due to invalid ranges or an excessive
    request of small or overlapping ranges.

    For byte ranges, failing to overlap the current extent means that the
    first-byte-pos of all of the byte-range-spec values were greater than
    the current length of the selected representation.  When this status
    code is generated in response to a byte-range request, the sender
    SHOULD generate a Content-Range header field specifying the current
    length of the selected representation (Section 4.2).

    For example:
        HTTP/1.1 416 Range Not Satisfiable
        Date: Fri, 20 Jan 2012 15:41:54 GMT
        Content-Range: bytes */47022

    Note: Because servers are free to ignore Range, many
    implementations will simply respond with the entire selected
    representation in a 200 (OK) response.  That is partly because
    most clients are prepared to receive a 200 (OK) to complete the
    task (albeit less efficiently) and partly because clients might
    not stop making an invalid partial request until they have
    received a complete representation.  Thus, clients cannot depend
    on receiving a 416 (Range Not Satisfiable) response even when it
    is most appropriate.

    Reference RFC 7233, Section 4.4

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '416 Range Not Satisfiable')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, resource_length, description=None, title=None,
                 headers={}, **kwargs):
        headers = {'Content-Range': 'bytes */' + str(resource_length)}
        super().__init__(416, description, title, headers, **kwargs)

class HTTPUnprocessableEntity(HTTPError):
    """422 Unprocessable Entity.

    The 422 (Unprocessable Entity) status code means the server
    understands the content type of the request entity (hence a
    415(Unsupported Media Type) status code is inappropriate), and the
    syntax of the request entity is correct (thus a 400 (Bad Request)
    status code is inappropriate) but was unable to process the contained
    instructions.  For example, this error condition may occur if an XML
    request body contains well-formed (i.e., syntactically correct), but
    semantically erroneous, XML instructions.

    Reference RFC 4918, Section 11.2

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '422 Unprocessable Entity')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(422, **kwargs)

class HTTPLocked(HTTPError):
    """423 Locked.

    The 423 (Locked) status code means the source or destination resource
    of a method is locked.  This response SHOULD contain an appropriate
    precondition or postcondition code, such as 'lock-token-submitted' or
    'no-conflicting-lock'.

    Reference RFC 4918, Section 11.3

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '423 Locked')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(423, **kwargs)

class HTTPFailedDependency(HTTPError):
    """424 Failed Dependency.

    The 424 (Failed Dependency) status code means that the method could
    not be performed on the resource because the requested action
    depended on another action and that action failed.

    Reference RFC 4918, Section 11.4

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '424 Failed Dependency')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(424, **kwargs)

class HTTPPreconditionRequired(HTTPError):
    """428 Precondition Required.

    The 428 status code indicates that the origin server requires the
    request to be conditional.

    Its typical use is to avoid the "lost update" problem, where a client
    GETs a resource's state, modifies it, and PUTs it back to the server,
    when meanwhile a third party has modified the state on the server,
    leading to a conflict.  By requiring requests to be conditional, the
    server can assure that clients are working with the correct copies.

    Responses using this status code SHOULD explain how to resubmit the
    request successfully.

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '424 Failed Dependency')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(42, **kwargs)

class HTTPTooManyRequests(HTTPError):
    """429 Too Many Requests.

    The HTTP 429 Too Many Requests response status code indicates the user
    has sent too many requests in a given amount of time ("rate limiting").
    A Retry-After header might be included to this response indicating how
    long to wait before making a new request.

    Reference  RFC 6585, Section 4

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '429 Too Many Requests.')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(429, **kwargs)

class HTTPRequestHeaderFieldsTooLarge(HTTPError):
    """431 Request Header Fields Too Large.

    The 431 status code indicates that the server is unwilling to process
    the request because its header fields are too large.  The request MAY
    be resubmitted after reducing the size of the request header fields.

    It can be used both when the set of request header fields in total is
    too large, and when a single header field is at fault.  In the latter
    case, the response representation SHOULD specify which header field
    was too large.

    Responses with the 431 status code MUST NOT be stored by a cache.

    Reference RFC 6585, Section 5

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '429 Too Many Requests.')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(429, **kwargs)


class HTTPUnavailableForLegalReasons(HTTPError):
    """451 Unavailable For Legal Reasons.

    451 Unavailable For Legal Reasons client error response code indicates that
    the user requested a resource that is not available due to legal reasons.

    A 451 response is cacheable by default; i.e., unless otherwise indicated by
    the method definition or explicit cache controls.

    Reference RFC 7725, Section 3

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '451 Unavailable For Legal Reasons')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(451, **kwargs)

class HTTPInternalServerError(HTTPError):
    """500 Internal Server Error.

    The server encountered an unexpected condition that prevented it
    from fulfilling the request.

    Reference RFC 7231, Section 6.6.1

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '500 Internal Server Error')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(500, **kwargs)

class HTTPNotImplemented(HTTPError):
    """501 Not Implemented.

    The 501 Not Implemented status code indicates that the server does
    not support the functionality required to fulfill the request.  This
    is the appropriate response when the server does not recognize the
    request method and is not capable of supporting it for any resource.

    A 501 response is cacheable by default unless otherwise indicated
    by the method definition or explicit cache controls as described
    in RFC 7234, Section 4.2.2.

    Reference RFC 7231, Section 6.6.2

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '501 HTTPNotImplemented')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(501, **kwargs)

class HTTPBadGateway(HTTPError):
    """502 Bad Gateway.

    The server, while acting as a gateway or proxy, received an invalid
    response from an inbound server it accessed while attempting to
    fulfill the request.

    Reference RFC 7231, Section 6.6.3

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '502 Bad Gateway')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(502, **kwargs)

class HTTPServiceUnavailable(HTTPError):
    """503 Service Unavailable.

    The server is currently unable to handle the request due to a
    temporary overload or scheduled maintenance, which will likely be
    alleviated after some delay.

    The server MAY send a Retry-After header field to suggest an
    appropriate amount of time for the client to wait before retrying
    the request.

    Note: The existence of the 503 status code does not imply that a
    server has to use it when becoming overloaded. Some servers might
    simply refuse the connection.

    Reference RFC 7231, Section 6.6.4

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '503 Service Unavailable')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(503, **kwargs)

class HTTPGatewayTimeout(HTTPError):
    """504 Gateway Timeout.

    The 504 Gateway Timeout status code indicates that the server,
    while acting as a gateway or proxy, did not receive a timely response
    from an upstream server it needed to access in order to complete the
    request.

    Reference RFC 7231, Section 6.6.5

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '504 Gateway Timeout')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(504, **kwargs)

class HTTPVersionNotSupported(HTTPError):
    """505 HTTP Version Not Supported

    The 505 HTTP Version Not Supported status code indicates that the
    server does not support, or refuses to support, the major version of
    HTTP that was used in the request message.  The server is indicating
    that it is unable or unwilling to complete the request using the same
    major version as the client (as described in RFC 7230, Section 2.6),
    other than with this error message.  The server SHOULD
    generate a representation for the 505 response that describes why
    that version is not supported and what other protocols are supported
    by that server.

    Reference RFC 7231, Section 6.6.6

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '505 HTTP Version Not Supported')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(505, **kwargs)

class HTTPInsufficientStorage(HTTPError):
    """507 Insufficient Storage.

    The 507 Insufficient Storage status code means the method could not
    be performed on the resource because the server is unable to store
    the representation needed to successfully complete the request. This
    condition is considered to be temporary. If the request that
    received this status code was the result of a user action, the
    request MUST NOT be repeated until it is requested by a separate user
    action.

    Reference RFC 4918, Section 11.5

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '507 Insufficient Storage')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(507, **kwargs)

class HTTPLoopDetected(HTTPError):
    """508 Loop Detected.

    The 508 Loop Detected status code indicates that the server
    terminated an operation because it encountered an infinite loop while
    processing a request with "Depth: infinity". This status indicates
    that the entire operation failed.

    Reference RFC 5842, Section 7.2

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '508 Loop Detected')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(508, **kwargs)

class HTTPNetworkAuthenticationRequired(HTTPError):
    """511 Network Authentication Required.

    The 511 status code indicates that the client needs to authenticate
    to gain network access.

    The response representation SHOULD contain a link to a resource that
    allows the user to submit credentials.

    Note that the 511 response SHOULD NOT contain a challenge or the
    authentication interface itself, because clients would show the
    interface as being associated with the originally requested URL,
    which may cause confusion.

    The 511 status SHOULD NOT be generated by origin servers; it is
    intended for use by intercepting proxies that are interposed as a
    means of controlling access to the network.

    Responses with the 511 status code MUST NOT be stored by a cache.

    Reference RFC 6585, Section 6

    Keyword Args:
        description (str): Human friendly description of the error.
        title (str): Error title (default '511 Network Authentication Required')
        headers (dict): A dict of header names and values to set.
        href (str): An href that can be used for more information.
    """
    def __init__(self, **kwargs):
        super().__init__(511, **kwargs)

class HTTPInvalidHeader(HTTPBadRequest):
    """Header in the request is invalid.

    Args:
        header_name (str): Header name.

    Keyword Args:
        msg (str): The actual reason for being invalid.
        title (str): Error title (default '400 Bad Request')
        href (str): An href that can be used for more information.
    """
    def __init__(self, header_name, msg='', title=None, href=None):
        description = "Value for header '%s'" % header_name + \
            "is invalid. %s" % msg
        super().__init__(description, title, href=href)

class HTTPMissingHeader(HTTPBadRequest):
    """Header is missing from the request.

    Args:
        header_name (str): Header name.

    Keyword Args:
        title (str): Error title (default '400 Bad Request')
        href (str): An href that can be used for more information.
    """

    def __init__(self, header_name, title=None, href=None):
        description = "Missing required header '%s'." % header_name
        super().__init__(description, title, href=href)


class HTTPInvalidQueryParam(HTTPBadRequest):
    """Query String parameter in the request is invalid.

    Args:
        param (str): Query string parameter.

    Keyword Args:
        title (str): Error title (default '400 Bad Request')
        href (str): An href that can be used for more information.
    """
    def __init__(self, param, title=None, href=None):
        description = "The URI query string '%s' parameter is invalid." % param
        super().__init__(description, title, href=href)

class HTTPMissingQueryParam(HTTPBadRequest):
    """Query String parameter in the request is invalid.

    Args:
        param (str): Query string parameter.

    Keyword Args:
        title (str): Error title (default '400 Bad Request')
        href (str): An href that can be used for more information.
    """
    def __init__(self, param, title=None, href=None):
        description = "The URI query string '%s' parameter is missing." % param
        super().__init__(description, title, href=href)

class HTTPInvalidFormField(HTTPBadRequest):
    """Form field in the request is invalid.

    Args:
        param (str): Query string parameter.

    Keyword Args:
        title (str): Error title (default '400 Bad Request')
        href (str): An href that can be used for more information.
    """
    def __init__(self, field, title=None, href=None):
        description = "The form field '%s' is invalid." % field
        super().__init__(description, title, href=href)

class HTTPMissingFormField(HTTPBadRequest):
    """Query String parameter in the request is invalid.

    Args:
        param (str): Query string parameter.

    Keyword Args:
        title (str): Error title (default '400 Bad Request')
        href (str): An href that can be used for more information.
    """
    def __init__(self, field, title=None, href=None):
        description = "The form field '%s' is missing." % field
        super().__init__(description, title, href=href)
